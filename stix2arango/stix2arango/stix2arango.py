import os
import json

import logging

from .. import config
from tqdm import tqdm
from ..services.arangodb_service import ArangoDBService
from jsonschema import validate


from .. import utils
module_logger = logging.getLogger("data_ingestion_service")


class Stix2Arango:

    def __init__(self, **kwargs):
        self.core_collection_vertex, self.core_collection_edge = (
            utils.get_vertex_and_edge_collection_names(kwargs.get("collection"))
        )
        EDGE_COLLECTIONS = [self.core_collection_edge]
        VERTEX_COLLECTIONS = [self.core_collection_vertex]

        self.arango = ArangoDBService(
            kwargs.get("database"),
            VERTEX_COLLECTIONS,
            EDGE_COLLECTIONS,
            create=True
        )

        self.file = kwargs.get("file")
        self.note = kwargs.get("stix2arango_note") if kwargs.get("stix2arango_note") else ""
        self.identity_ref = json.loads(utils.load_file_from_url(config.STIX2ARANGO_IDENTITY))
        self.marking_definition_refs = [json.loads(utils.load_file_from_url(link)) for link in config.MARKING_DEFINITION_REFS]
        self.bundle_id = utils.read_file_data(self.file).get("id")
        self.ignore_embedded_relationships = eval(kwargs.get("ignore_embedded_relationships").capitalize()) if kwargs.get("ignore_embedded_relationships", None) else False


    def default_objects(self):
        object_list = []
        for obj in config.DEFAULT_OBJECT_URL:
            data = json.loads(utils.load_file_from_url(obj))
            object_list.append(data)

        for obj in utils.read_file_data("templates/marking-definition.json"):
            object_list.append(obj)
        return object_list

    def is_latest_actually_latest(self, results, sort_by, collection):
        if len(results)>0:
            if sort_by == "doc.modified":
                query = "FOR doc IN {} " \
                        "FILTER doc.id=='{}' " \
                        "AND doc._is_latest==False " \
                        "AND doc.modified=='{}' " \
                        "return doc" \
                        "".format(
                            collection,
                            results[0].get("id"),
                            results[0].get("modified")
                        )
                results = self.arango.execute_raw_query(query)
                return len(results)>1
        return False


    def get_is_latest(self, data, collection):

        for _type, obj, modified in tqdm(data):
            sort_by = "doc._record_modified"
            if modified:
                sort_by = "doc.modified"

            query = "FOR doc IN {} FILTER doc.id=='{}' AND doc._is_latest==False " \
                    "SORT {} " \
                    "DESC LIMIT 1 return doc".format(collection, obj, sort_by)
            results = self.arango.execute_raw_query(query)

            if modified:
                if self.is_latest_actually_latest(results, sort_by, collection):
                    sort_by = "doc._record_modified"
                    query = "FOR doc IN {} FILTER doc.id=='{}' AND doc._is_latest==False " \
                            "SORT {} " \
                            "DESC LIMIT 1 return doc".format(collection, obj, sort_by)
                    results = self.arango.execute_raw_query(query)

            if len(results) == 1 and results[0].get("_key") != obj:
                query = \
                    "FOR doc IN {} FILTER doc._key=='{}' " \
                    "remove doc in {}".format(collection, results[0].get("_key"), collection)

                self.arango.execute_raw_query(query)
                result = results[0]
                result['_key'] = result['_key'].split("+")[0]
                result['_id'] = result['_id'].split("+")[0]
                result['_is_latest'] = True
                query = f"INSERT {json.dumps(result)} INTO {collection}"
                self.arango.execute_raw_query(query)

    def process_bundle_into_graph(self, filename: str, data=None, notes=None):
        module_logger.info(f"Reading vertex from file {self.file} now")
        if not data:
            with open(filename, "r") as input_file:
                file_data = input_file.read()
                try:
                    data = json.loads(file_data)
                except Exception as e:
                    raise Exception("Invalid file type")

            try:
                validate(instance=data, schema=config.json_schema)
            except Exception as e:
                raise Exception("Invalid File structure")

        if data.get("type", None) != "bundle":
            module_logger.error("Provided file is not a STIX bundle. Aborted")
            return False

        objects = []; insert_data = []  # That would be the overall statement
        for obj in tqdm(data["objects"]):
            if obj.get("type") not in ["relationship"]:
                obj['_bundle_id'] = self.bundle_id if filename!= "" else ""
                obj['_file_name'] = os.path.basename(filename) if len(filename.split("/"))>1 else ""
                obj['_stix2arango_note'] = notes if notes else self.note
                obj['_record_md5_hash'] = utils.generate_md5(obj)
                # self.arango.formulate_insert_statement(obj, insert_statement,
                #                                        self.core_collection_vertex)
                objects.append(obj)
                insert_data.append([
                        obj.get("type"), obj.get("id"),
                        True if "modified" in obj else False])

        module_logger.info(f"Inserting objects into database. Total objects: {len(objects)}")
        self.arango.upsert_several_objects_chunked(objects, self.core_collection_vertex)

        self.get_is_latest(insert_data, self.core_collection_vertex)

    def map_relationships(self, filename):
        with open(filename, "r") as input_file:
            file_data = input_file.read()
            data = json.loads(file_data)

        if data.get("type", None) != "bundle":
            module_logger.error("Provided file is not a STIX bundle. Aborted")
            return False
        module_logger.info("Mapping Prebuilt Relationship Objects -> ")
        insert_statement = []; inserted_data = []
        for obj in tqdm(data["objects"]):
            if obj.get("type") == "relationship":

                source_ref = obj.get("source_ref")
                target_ref = obj.get("target_ref")
                if not self.core_collection_vertex:
                    module_logger.info(f"source_ref_collection_name is not found: {obj}")
                    continue
                if not self.core_collection_vertex:
                    module_logger.info(f"target_ref_collection_name is not found: {obj}")
                    continue
                obj["_from"] = f"{self.core_collection_vertex}/{source_ref}"
                obj["_to"] = f"{self.core_collection_vertex}/{target_ref}"
                obj['_bundle_id'] = data.get("id")
                obj['_file_name'] = os.path.basename(filename) if len(filename.split("/"))>1 else ""
                obj['_stix2arango_note'] = self.note
                # obj['_record_created'] = obj.get("created")
                # obj['_record_modified'] = utils.get_object_details(obj, self)
                obj['_is_ref'] = False
                obj['_record_md5_hash'] = utils.generate_md5(obj)
                # self.arango.formulate_insert_statement(
                #     obj, insert_statement, self.core_collection_edge
                # )
                insert_statement.append(obj)
                inserted_data.append([obj.get("type"), obj.get("id"), True if "modified" in obj else False])

        module_logger.info(f"Inserting relationship into database. Total objects: {len(insert_statement)}")
        self.arango.upsert_several_objects_chunked(insert_statement, self.core_collection_edge)
        self.get_is_latest(inserted_data, self.core_collection_edge)


        if not self.ignore_embedded_relationships:
            module_logger.info("Creating new embedded relationships using _refs and _ref")
            insert_statement = [];inserted_data = []
            for obj in tqdm(data["objects"]):
                filtered_keys = config.refs_list
                for key in filtered_keys:
                    if key in list(obj.keys()):
                        target = obj.get(key)
                        if isinstance(obj.get(key), str):
                            target = [obj.get(key)]
                        inserted_data+=utils.create_relationship_obj(
                            obj=obj,
                            source=obj.get("id"),
                            targets=target,
                            relationship=key,
                            arango_obj=self,
                            bundle_id=data["id"],
                            insert_statement = insert_statement
                        )
            module_logger.info(f"Inserting embedded relationship into database. Total objects: {len(insert_statement)}")
            self.arango.upsert_several_objects_chunked(insert_statement, self.core_collection_edge)
            self.get_is_latest(inserted_data, self.core_collection_edge)

    def run(self):
        module_logger.info(f"Loading default objects from url and store into {self.core_collection_vertex}")
        self.process_bundle_into_graph(
            filename="",
            data={
                "type": "bundle",
                "objects": self.default_objects()
            },
            notes="automatically imported on collection creation"
        )

        module_logger.info(f"Load objects from file: {self.file} and store into {self.core_collection_vertex}")
        self.process_bundle_into_graph(
            filename=self.file
        )
        module_logger.info("Mapping relationships now -> ")
        self.map_relationships(
            filename=self.file
        )
