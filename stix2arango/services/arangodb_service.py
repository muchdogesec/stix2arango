import os
import json
import logging
import time
from typing import Any
import arango.database
from arango.collection import StandardCollection
from arango import ArangoClient
from arango.exceptions import ArangoServerError

from datetime import datetime, timezone
from tqdm import tqdm

from .. import config
from .. import utils
from pprint import pprint

module_logger = logging.getLogger("data_ingestion_service")


class ArangoDBService:
    ALWAYS_LATEST = os.getenv('ALWAYS_LATEST', False)


    def __init__(self, db, vertex_collections, edge_collections, relationship=None, create=False, username=None, password=None, host_url=None, always_latest=ALWAYS_LATEST, **kwargs):
        self.ARANGO_DB = self.get_db_name(db)
        self.ARANGO_GRAPH = f"{self.ARANGO_DB.split('_database')[0]}_graph"
        self.COLLECTIONS_VERTEX = vertex_collections
        self.COLLECTIONS_EDGE = edge_collections
        self.FORCE_RELATIONSHIP = [relationship] if relationship else None
        self.missing_collection = True
        self.ALWAYS_LATEST = always_latest

        module_logger.info("Establishing connection...")
        client = ArangoClient(hosts=host_url)
        self._client = client

        self.sys_db = client.db(
            "_system", username=username, password=password
        )

        module_logger.info("_system database - OK")

        if not self.sys_db.has_database(self.ARANGO_DB):
            if create:
                self.create_database(self.ARANGO_DB)
            else:
                raise Exception("Database not found")

        self.db = client.db(
            self.ARANGO_DB,
            username=username,
            password=password,
            verify=True
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
                    module_logger.debug(f"create edge collection {collection} failed with {e}")
            
            self.cti2stix_objects_relationship = (
                    self.cti2stix_graph.edge_collection(collection)
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
        except arango.exceptions.CollectionCreateError:
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
            obj["_key"] = obj.get('_key', f'{obj["id"]}+{now}')
            if self.ALWAYS_LATEST:
                obj['_is_latest'] = True

        query = """
            //LET obj_map = ZIP(@objects[*].id, @objects[*]._record_md5_hash) //make a map so we don't have to do `CONTAINS(ARRAY[60000000], id)`
            LET obj_map = MERGE_RECURSIVE(
                FOR obj in @objects
                RETURN {[obj.id]: obj._record_md5_hash}
            )
            LET existing_objects = MERGE(
                FOR doc in @@collection FILTER doc.id IN KEYS(obj_map) AND doc._record_md5_hash == obj_map[doc.id]
                // FILTER [doc._from, doc._to] == obj_map[doc.id][doc._record_md5_hash]
                LET obj_hashkey = CONCAT(doc.id, ";", doc._record_md5_hash)
                RETURN {[obj_hashkey]: doc._id}
            )
            
            LET inserted_objects = (
                FOR object in @objects
                LET obj_hashkey = CONCAT(object.id, ";", object._record_md5_hash)
                FILTER NOT HAS(existing_objects, obj_hashkey)
                INSERT object INTO @@collection
                RETURN object.id
            )
            
            RETURN {inserted_objects, existing_objects}
        """
        result = self.execute_raw_query(query, bind_vars={
            "@collection": collection_name,
            "objects": objects
        })[0]
        return result['inserted_objects'], result['existing_objects']

    def insert_several_objects_chunked(self, objects, collection_name, chunk_size=1000, remove_duplicates=True):
        if remove_duplicates:
            original_length = len(objects)
            objects = utils.remove_duplicates(objects)
            logging.info("removed {count} duplicates from imported objects.".format(count=original_length-len(objects)))
        
        progress_bar = tqdm(utils.chunked(objects, chunk_size), total=len(objects), desc='insert_several_objects_chunked')
        inserted_objects = []
        existing_objects = {}
        for chunk in progress_bar:
            inserted, existing = self.insert_several_objects(chunk, collection_name)
            inserted_objects.extend(inserted)
            existing_objects.update(existing)
            progress_bar.update(len(chunk))
        return inserted_objects, existing_objects
    
    def insert_relationships_chunked(self, relationships: list[dict[str, Any]], id_to_key_map: dict[str, str], collection_name: str, chunk_size=1200):
        for relationship in relationships:
            source_key = id_to_key_map.get(relationship['source_ref'])
            target_key = id_to_key_map.get(relationship['target_ref'])
            
            relationship['_stix2arango_ref_err'] = not (target_key and source_key)
            relationship['_from'] = source_key or relationship['_from']
            relationship['_to'] = target_key or relationship['_to']
            relationship['_record_md5_hash'] = relationship.get('_record_md5_hash', utils.generate_md5(relationship))
        return self.insert_several_objects_chunked(relationships, collection_name, chunk_size=chunk_size)

    def update_is_latest_several(self, object_ids, collection_name):
        #returns newly deprecated _ids
        query = """
            LET matched_objects = ( // collect all the modified into a single list of {id: ?, modified: ?, _record_modified: ?, _key: ?}
                FOR object in @@collection FILTER object.id IN @object_ids
                RETURN KEEP(object, 'id', 'modified', '_record_modified', '_key', '_id')
            )
            
            LET modified_map = MERGE( // get max modified by ID
                FOR object in matched_objects
                COLLECT id = object.id INTO objects_by_id
                RETURN (
                    FOR id_obj  in objects_by_id[*]
                        SORT id_obj.object.modified DESC, id_obj.object._record_modified DESC
                        LIMIT 1
                        RETURN {[id]: id_obj.object._key}
                    )[0]
            )
            
            
            FOR doc IN matched_objects
            LET _is_latest = modified_map[doc.id] == doc._key
            UPDATE {_key: doc._key, _is_latest} IN @@collection
            FILTER _is_latest != doc._is_latest AND _is_latest == FALSE
            RETURN doc._id
        """
        return self.execute_raw_query(query, bind_vars={
            "@collection": collection_name,
            "object_ids": object_ids,
        })
    
    def update_is_latest_several_chunked(self, object_ids, collection_name, edge_collection=None, chunk_size=500):
        if self.ALWAYS_LATEST:
            logging.debug('Skipped update _is_latest')
            return []
        logging.info(f"Updating _is_latest for {len(object_ids)} newly inserted items")
        progress_bar = tqdm(utils.chunked(object_ids, chunk_size), total=len(object_ids), desc='update_is_latest_several_chunked')
        deprecated_key_ids = [] # contains newly deprecated _ids
        for chunk in progress_bar:
            deprecated_key_ids.extend(self.update_is_latest_several(chunk, collection_name))
            progress_bar.update(len(chunk))

        logging.info(f"Updating relationship's _is_latest for {len(deprecated_key_ids)} items")
        self.deprecate_relationships(deprecated_key_ids, edge_collection)
        return deprecated_key_ids
    
    def deprecate_relationships(self, deprecated_key_ids: list, edge_collection: str):
        deprecation_count = 0
        query = """
        FOR doc IN @@collection
        FILTER doc._from IN @deprecated_key_ids AND doc._is_latest
        UPDATE {_key: doc._key, _is_latest: FALSE} IN @@collection
        FILTER doc._is_ref != TRUE // no need for further propagation for embedded relationships
        RETURN doc._id
        """
        # logging.info("deprecating relationships for %d objects", len(deprecated_key_ids))

        while deprecated_key_ids and edge_collection:
            deprecated_key_ids = self.execute_raw_query(query, bind_vars={
                "@collection": edge_collection,
                "deprecated_key_ids": deprecated_key_ids,
            })
            deprecation_count += len(deprecated_key_ids)

        if deprecation_count:
            logging.info("deprecated %d relationships", deprecation_count)
        
        return deprecation_count

    @staticmethod
    def get_db_name(name):
        ENDING = "_database"
        if name.endswith(ENDING):
            return name
        return name + ENDING
