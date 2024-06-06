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


    def insert_several_objects(self, objects: list[dict], collection_name: str) -> None:
        if not collection_name:
            module_logger.info(f"Object has unknown type: {objects}")
            return

        for _, obj in enumerate(objects):
            obj["_is_latest"] = False
            obj["_record_created"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
            obj["_record_modified"] = obj["_record_created"]
            obj["_key"] = f'{obj["id"]}+{obj.get('_record_modified')}'

        query = """
            LET obj_map = ZIP(@objects[*].id, @objects[*]._record_md5_hash) //make a map so we don't have to do `CONTAINS(ARRAY[60000000], id)`
            LET existing_objects = MERGE(
                FOR doc in @@collection
                FILTER obj_map[doc.id] == doc._record_md5_hash
                RETURN {[doc.id]: TRUE}
            )
            
            FOR object in @objects
            FILTER existing_objects[object.id] != TRUE
            INSERT object INTO @@collection
            RETURN object.id
        """
        return self.execute_raw_query(query, bind_vars={
            "@collection": collection_name,
            "objects": objects
        })

    def insert_several_objects_chunked(self, objects, collection_name, chunk_size=1000):
        progress_bar = tqdm(utils.chunked(objects, chunk_size), total=len(objects))
        results = []
        for chunk in progress_bar:
            results.extend(self.insert_several_objects(chunk, collection_name))
            progress_bar.update(len(chunk))
        return results

    def update_is_latest_several(self, object_ids, collection_name):
        objects_in = {k: True for k  in object_ids}
        query = """
            LET matched_objects = ( // collect all the modified into a single list of {id: ?, modified: ?}
                FOR object in @@collection
                FILTER @objects_in[object.id] !=  NULL
                RETURN {id: object.id, modified: (object.modified OR object._record_modified), _key: object._key}
            )
            
            LET modified_map = MERGE( // get max modified by ID
                FOR object in matched_objects
                COLLECT id = object.id INTO objects_by_id
                RETURN {[id]: MAX(objects_by_id[*].object.modified)}
            )
            
            FOR doc IN matched_objects
            LET _is_latest = doc.modified == modified_map[doc.id]
            UPDATE {_key: doc._key, _is_latest} IN @@collection
        """
        return self.execute_raw_query(query, bind_vars={
            "@collection": collection_name,
            "objects_in": objects_in
        })
    
    def update_is_latest_several_chunked(self, object_ids, collection_name, chunk_size=500):
        logging.info(f"Updating _is_latest for {len(object_ids)} newly inserted items")
        progress_bar = tqdm(utils.chunked(object_ids, chunk_size), total=len(object_ids))
        for chunk in progress_bar:
            self.update_is_latest_several(chunk, collection_name)
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
