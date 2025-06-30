import contextlib
import os
import json
import logging
import re
import time
from typing import Any
import arango.database
from arango.collection import StandardCollection
from arango import ArangoClient
from arango.exceptions import ArangoServerError

from datetime import datetime, timezone
from tqdm import tqdm

from stix2arango.services.version_annotator import annotate_versions

from .. import config
from .. import utils
from pprint import pprint

module_logger = logging.getLogger("data_ingestion_service")


class ArangoDBService:

    def __init__(
        self,
        db,
        vertex_collections,
        edge_collections,
        relationship=None,
        create_db=False,
        create=False,
        username=None,
        password=None,
        host_url=None,
        **kwargs,
    ):
        self.ARANGO_DB = self.get_db_name(db)
        self.ARANGO_GRAPH = f"{self.ARANGO_DB.split('_database')[0]}_graph"
        self.COLLECTIONS_VERTEX = vertex_collections
        self.COLLECTIONS_EDGE = edge_collections
        self.FORCE_RELATIONSHIP = [relationship] if relationship else None
        self.missing_collection = True

        module_logger.info("Establishing connection...")
        client = ArangoClient(hosts=host_url)
        self._client = client

        if create_db:
            module_logger.info(f"create db `{self.ARANGO_DB}` if not exist")
            self.sys_db = client.db("_system", username=username, password=password)

            module_logger.info("_system database - OK")

            if not self.sys_db.has_database(self.ARANGO_DB):
                self.create_database(self.ARANGO_DB)

        self.db = client.db(
            self.ARANGO_DB, username=username, password=password, verify=True
        )

        if self.db.has_graph(self.ARANGO_GRAPH):
            self.cti2stix_graph = self.db.graph(self.ARANGO_GRAPH)
        elif create:
            self.cti2stix_graph = self.db.create_graph(self.ARANGO_GRAPH)

        self.collections: dict[str, StandardCollection] = {}
        for collection in self.COLLECTIONS_VERTEX:
            if create:
                self.collections[collection] = self.create_collection(collection)

            self.collections[collection] = self.db.collection(collection)

        for collection in self.COLLECTIONS_EDGE:

            if create:
                try:
                    self.cti2stix_objects_relationship = (
                        self.cti2stix_graph.create_edge_definition(
                            edge_collection=collection,
                            from_vertex_collections=self.COLLECTIONS_VERTEX,
                            to_vertex_collections=self.COLLECTIONS_VERTEX,
                        )
                    )
                except Exception as e:
                    module_logger.debug(
                        f"create edge collection {collection} failed with {e}"
                    )

            self.cti2stix_objects_relationship = self.cti2stix_graph.edge_collection(
                collection
            )
            self.collections[collection] = self.cti2stix_objects_relationship

        module_logger.info("ArangoDB Connected now!")

    def create_database(self, db_name):
        try:
            self.sys_db.create_database(db_name)
        except arango.exceptions.DatabaseCreateError as e:
            module_logger.debug(f"create database {db_name} failed with {e}")

    def create_collection(self, collection_name):
        try:
            return self.db.create_collection(collection_name)
        except arango.exceptions.CollectionCreateError as e:
            module_logger.warning(
                f"create collection {collection_name} failed with {e}"
            )
            return self.db.collection(collection_name)

    def execute_raw_query(self, query: str, bind_vars=None, **kwargs) -> list:
        try:
            cursor = self.db.aql.execute(query, bind_vars=bind_vars, **kwargs)
            result = [doc for doc in cursor]
            return result
        except arango.exceptions.AQLQueryExecuteError:
            module_logger.error(f"AQL exception in the query: {query}")
            raise

    def insert_several_objects(self, objects: list[dict], collection_name: str) -> None:
        if not collection_name:
            module_logger.info(f"Object has unknown type: {objects}")
            return

        for _, obj in enumerate(objects):
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            obj["_is_latest"] = False
            obj["_record_created"] = obj.get("_record_created", now)
            obj["_record_modified"] = now
            obj["_key"] = obj.get("_key", f'{obj["id"]}+{now}')

            if obj["type"] == "relationship":
                obj.update(
                    _target_type=obj["target_ref"].split("--")[0],
                    _source_type=obj["source_ref"].split("--")[0],
                )
        new_insertions = objects #[obj for obj in objects if f'{obj["id"]};{obj["_record_md5_hash"]}' not in existing_objects]
        existing_objects = {}

        d = self.db.collection(collection_name).insert_many(new_insertions, overwrite_mode="ignore", sync=True)
        for i, ret in enumerate(d):
            obj = objects[i]
            if isinstance(ret, arango.exceptions.DocumentInsertError):
                if ret.error_code == 1210:
                    existing_objects[f'{obj["id"]};{obj["_record_md5_hash"]}'] = collection_name + '/' + re.search(r'conflicting key: (.*)', ret.message).group(1)
                    if 'relationship--7a1682a3-fec3-53ed-8dd5-68f54b1d6f7a' in ret.message:
                        print(1)
                else:
                    raise ret
        return [obj["id"] for obj in new_insertions], existing_objects

    def insert_several_objects_chunked(
        self, objects, collection_name, chunk_size=1000, remove_duplicates=True
    ):
        if remove_duplicates:
            original_length = len(objects)
            objects = utils.remove_duplicates(objects)
            logging.info(
                "removed {count} duplicates from imported objects.".format(
                    count=original_length - len(objects)
                )
            )

        progress_bar = tqdm(
            utils.chunked(objects, chunk_size),
            total=len(objects),
            desc="insert_several_objects_chunked",
        )
        inserted_objects = []
        existing_objects = {}
        for chunk in progress_bar:
            inserted, existing = self.insert_several_objects(chunk, collection_name)
            inserted_objects.extend(inserted)
            existing_objects.update(existing)
            progress_bar.update(len(chunk))
        return inserted_objects, existing_objects

    def insert_relationships_chunked(
        self,
        relationships: list[dict[str, Any]],
        id_to_key_map: dict[str, str],
        collection_name: str,
        chunk_size=1200,
    ):
        for relationship in relationships:
            source_key = id_to_key_map.get(relationship["source_ref"])
            target_key = id_to_key_map.get(relationship["target_ref"])

            relationship["_stix2arango_ref_err"] = not (target_key and source_key)
            relationship["_from"] = self.fix_edge_ref(source_key or relationship["_from"])
            relationship["_to"] = self.fix_edge_ref(target_key or relationship["_to"])
            relationship["_record_md5_hash"] = relationship.get(
                "_record_md5_hash", utils.generate_md5(relationship)
            )
        return self.insert_several_objects_chunked(
            relationships, collection_name, chunk_size=chunk_size
        )
    
    @staticmethod
    def fix_edge_ref(_id):
        c, _, _key = _id.partition('/')
        if not c:
            c = "missing_collection"
        return f"{c}/{_key}"

    def update_is_latest_several(self, object_ids, collection_name):
        # returns newly deprecated _ids
        query = """
            FOR doc IN @@collection OPTIONS {indexHint: "s2a_search", forceIndexHint: true}
            FILTER doc.id IN @object_ids
            RETURN [doc.id, doc._key, doc.modified, doc._record_modified, doc._is_latest, doc._id]
        """
        out = self.execute_raw_query(
            query,
            bind_vars={
                "@collection": collection_name,
                "object_ids": object_ids,
            },
        )
        out = [dict(zip(('id', '_key', 'modified', '_record_modified', '_is_latest', '_id'), obj_tuple)) for obj_tuple in out]
        annotated, deprecated = annotate_versions(out)
        self.db.collection(collection_name).update_many(annotated, sync=True, keep_none=False)
        return deprecated



    def update_is_latest_several_chunked(
        self, object_ids, collection_name, edge_collection=None, chunk_size=5000
    ):
        logging.info(f"Updating _is_latest for {len(object_ids)} newly inserted items")
        progress_bar = tqdm(
            utils.chunked(object_ids, chunk_size),
            total=len(object_ids),
            desc="update_is_latest_several_chunked",
        )
        deprecated_key_ids = []  # contains newly deprecated _ids
        for chunk in progress_bar:
            deprecated_key_ids.extend(
                self.update_is_latest_several(chunk, collection_name)
            )
            progress_bar.update(len(chunk))

        logging.info(
            f"Updating relationship's _is_latest for {len(deprecated_key_ids)} items"
        )
        self.deprecate_relationships(deprecated_key_ids, edge_collection)
        return deprecated_key_ids

    def deprecate_relationships(
        self, deprecated_key_ids: list, edge_collection: str, chunk_size=5000
    ):
        keys = self.get_relationships_to_deprecate(deprecated_key_ids, edge_collection)
        self.db.collection(edge_collection).update_many(
            tuple(dict(_key=_key, _is_latest=False) for _key in keys),
            silent=True,
            raise_on_document_error=True,
        )
        return len(keys)

    def get_relationships_to_deprecate(
        self, deprecated_key_ids: list, edge_collection: str
    ):
        query = """
        FOR doc IN @@collection OPTIONS {indexHint: "s2a_search_edge", forceIndexHint: true}
        FILTER doc._from IN @deprecated_key_ids AND doc._is_latest == TRUE
        RETURN doc._id
        """
        items_to_deprecate_full: set[str] = {*deprecated_key_ids}

        while deprecated_key_ids:
            deprecated_key_ids = self.execute_raw_query(
                query,
                bind_vars={
                    "@collection": edge_collection,
                    "deprecated_key_ids": deprecated_key_ids,
                },
            )
            items_to_deprecate_full.update(deprecated_key_ids)
        return [_id.split("/", 1)[1] for _id in items_to_deprecate_full]

    @staticmethod
    def get_db_name(name):
        ENDING = "_database"
        if name.endswith(ENDING):
            return name
        return name + ENDING
    
    @contextlib.contextmanager
    def transactional(self, write=None, exclusive=None, sync=True):
        original_db = self.db
        transactional_db = self.db.begin_transaction(allow_implicit=True, write=write, exclusive=exclusive, sync=sync)
        try:
            self.db = transactional_db
            yield self
            transactional_db.commit_transaction()
        except:
            transactional_db.abort_transaction()
            raise
        finally:
            self.db = original_db
