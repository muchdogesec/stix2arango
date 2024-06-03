import os
import json
import logging
import time
import arango.database
from arango import ArangoClient
from arango.exceptions import ArangoServerError

from datetime import datetime
from tqdm import tqdm

from .. import config
from .. import utils
from pprint import pprint

module_logger = logging.getLogger("data_ingestion_service")


class ArangoDBService:

    def __init__(self, db, vertex_collections, edge_collections, relationship=None, create=False):
        self.ARANGO_DB = self.get_db_name(db)
        self.ARANGO_GRAPH = f"{self.ARANGO_DB.split('_database')[0]}_graph"
        self.COLLECTIONS_VERTEX = vertex_collections
        self.COLLECTIONS_EDGE = edge_collections
        self.FORCE_RELATIONSHIP = [relationship] if relationship else None
        self.missing_collection = True

        module_logger.info("Establishing connection...")
        client = ArangoClient(hosts=f"http://{config.ARANGODB_HOST}:{config.ARANGODB_PORT}")

        sys_db = client.db(
            "_system", username=config.ARANGODB_USERNAME, password=config.ARANGODB_PASSWORD
        )

        module_logger.info("_system database - OK")

        if not sys_db.has_database(self.ARANGO_DB):
            if create:
                sys_db.create_database(self.ARANGO_DB)
            else:
                raise Exception("Database not found")

        self.db = client.db(
            self.ARANGO_DB,
            username=config.ARANGODB_USERNAME,
            password=config.ARANGODB_PASSWORD,
        )

        if self.db.has_graph(self.ARANGO_GRAPH):
            self.cti2stix_graph = self.db.graph(self.ARANGO_GRAPH)
        elif create:
            self.cti2stix_graph = self.db.create_graph(self.ARANGO_GRAPH)

        self.collections = {}
        for collection in self.COLLECTIONS_VERTEX:
            if self.db.has_collection(collection):
                self.collections[collection] = self.db.collection(collection)
            elif create:
                self.collections[collection] = self.db.create_collection(collection)
            else:
                raise Exception(f"Vertex collection missing: {collection}")

        for collection in self.COLLECTIONS_EDGE:
            if self.cti2stix_graph.has_edge_definition(collection):
                self.cti2stix_objects_relationship = (
                    self.cti2stix_graph.edge_collection(collection)
                )
            elif create:
                self.cti2stix_objects_relationship = (
                    self.cti2stix_graph.create_edge_definition(
                        edge_collection=collection,
                        from_vertex_collections=self.COLLECTIONS_VERTEX,
                        to_vertex_collections=self.COLLECTIONS_VERTEX,
                    )
                )
            else:
                raise Exception(f"Edges collection missing: {collection}")


        module_logger.info("ArangoDB Connected now!")

    def create_if_not_exist(self, collection_name):
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

    def upsert_several_objects(self, objects: list[dict], collection_name: str) -> None:
        if not collection_name:
            module_logger.info(f"Object has unknown type: {objects}")
            return

        for _, obj in enumerate(objects):
            if not obj.get("_key"):
                obj["_key"] = obj["id"]
            if not obj.get("_is_latest"):
                obj["_is_latest"] = False
            obj["_record_created"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
            obj["_record_modified"] = obj["_record_created"]
            obj["_id"] = "{}+{}".format(
                obj["id"], datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
            )
        query = """
            LET objects = ( FOR new_doc in @objects
            LET old_doc = DOCUMENT(CONCAT(@collection_name, "/", new_doc.id))
            RETURN {new_doc, old_doc}
            )

            LET old_reinserts = (FOR obj in objects
            FILTER obj.old_doc != NULL AND obj.old_doc._record_md5_hash != obj.new_doc._record_md5_hash //Only update if the old_record_md5_hash does not match _record_md5_hash
            LET __reinsert_key = CONCAT(obj.old_doc._key, "+", DATE_ISO8601(DATE_NOW()))
            RETURN MERGE(obj.old_doc, {_key: __reinsert_key, __reinsert_key})
            )

            LET new_inserts = (FOR obj in objects
            FILTER obj.old_doc == NULL
            RETURN obj.new_doc
            )

            FOR item in APPEND(new_inserts, old_reinserts)
            LET __reinsert_key = item.__reinsert_key
            LET doc = UNSET(item, "__reinsert_key", "_id")
            UPSERT {_key: doc._key}
            INSERT doc
            REPLACE doc INTO @@collection_name

            FILTER __reinsert_key != NULL // ONLY RETUURN VALUES THAT WERE REINSERTED
            RETURN [doc.id, doc._key]
        """
        return self.execute_raw_query(query, bind_vars={
            "@collection_name": collection_name,
            "collection_name": collection_name,
            "objects": objects
        })

    def upsert_several_objects_chunked(self, objects, collection_name, chunk_size=1000):
        def chunked(iterable, n):
            for i in range(0, len(iterable), n):
                yield iterable[i : i + n]

        progress_bar = tqdm(chunked(objects, chunk_size), total=len(objects), ncols=50)
        for chunk in progress_bar:
            self.upsert_several_objects(chunk, collection_name)
            progress_bar.update(len(chunk))
    
    def validate_collections(self):
        prebuilt_collections = [
            collection.get("name")
            for collection in self.db.collections()
            if not collection.get("system")
        ]
        if utils.validate_collections(prebuilt_collections):
            self.missing_collection = False
            return None



    def map_relationships(self, data, func, collection_vertex, collection_edge, notes):
        insert_data = []
        for obj in tqdm(data):
            if obj.get("type") not in [
                "relationship",
                "report",
                "identity",
                "marking-definition",
            ]:
                # noinspection PyUnresolvedReferences
                insert_data += func(
                    obj, self, collection_vertex, collection_edge, notes
                )
        return insert_data

    def filter_objects_in_collection_using_custom_query(
        self, collection_name: str = None, custom_query: str = ""
    ):

        query = f"FOR doc IN {collection_name} "
        query += custom_query
        query += "RETURN doc"
        # print(query)
        try:
            cursor = self.db.aql.execute(query)
            result = [doc for doc in cursor]
            return result
        except arango.exceptions.AQLQueryExecuteError:
            module_logger.error(f"AQL exception in the query: {query}")
            raise

    def filter_objects_in_list_collection_using_custom_query(
        self, collection_list: list = [], filters: str = ""
    ):
        subqueries = ""
        for collection in collection_list:
            subqueries += " let %s = (for t in %s %s return t)" % (
                collection,
                collection,
                filters,
            )
        collection_ = ", ".join(collection_list)
        query = (
            "LET results = (%s For doc IN UNION (%s) RETURN doc ) RETURN results"
            % (subqueries, collection_)
        )
        try:
            cursor = self.db.aql.execute(query)
            result = [doc for doc in cursor]
            return result
        except arango.exceptions.AQLQueryExecuteError:
            module_logger.error(f"AQL exception in the query: {query}")
            raise

    @staticmethod
    def get_db_name(name):
        ENDING = "_database"
        if name.endswith(ENDING):
            return name
        return name + ENDING
