from datetime import datetime
import os
import json

import logging
from pathlib import Path
import pkgutil
import re
import time
import uuid

from .bundle_loader import BundleLoader

from .. import config
from tqdm import tqdm
from ..services.arangodb_service import ArangoDBService
from jsonschema import validate
from arango.collection import StandardCollection


from .. import utils

module_logger = logging.getLogger("data_ingestion_service")
SMO_TYPES = ["marking-definition", "extension-definition", "language-content"]


class Stix2Arango:
    EMBEDDED_RELATIONSHIP_RE = re.compile(r"([a-z\-_]+)[_\-]refs{0,1}")
    filename = "bundle.json"
    ARANGODB_URL = f"http://{config.ARANGODB_HOST}:{config.ARANGODB_PORT}"

    def __init__(
        self,
        database,
        collection,
        file,
        create_collection=True,
        create_db=True,
        stix2arango_note="",
        ignore_embedded_relationships=False,
        ignore_embedded_relationships_sro=True,
        ignore_embedded_relationships_smo=True,
        bundle_id=None,
        username=config.ARANGODB_USERNAME,
        password=config.ARANGODB_PASSWORD,
        host_url=ARANGODB_URL,
        is_large_file=False,
        skip_default_indexes=False,
        create_taxii_views=True,
        **kwargs,
    ):
        """
        `modify_fn` should modify in-place, returned value is discarded
        """
        
        self.alter_functions = []
        
        self.core_collection_vertex, self.core_collection_edge = (
            utils.get_vertex_and_edge_collection_names(collection)
        )
        EDGE_COLLECTIONS = [self.core_collection_edge]
        VERTEX_COLLECTIONS = [self.core_collection_vertex]

        self.arango = ArangoDBService(
            database,
            VERTEX_COLLECTIONS,
            EDGE_COLLECTIONS,
            create=create_collection,
            create_db=create_db,
            username=username,
            password=password,
            host_url=host_url,
            **kwargs,
        )

        self.arangodb_extra_data = {}

        self.file = file
        self.is_large_file = is_large_file
        self.note = stix2arango_note or ""
        self.identity_ref = utils.load_file_from_url(config.STIX2ARANGO_IDENTITY)
        self.default_ref_objects = [
            utils.load_file_from_url(link)
            for link in config.MARKING_DEFINITION_REFS + config.IDENTITY_REFS
        ]
        self.bundle_id = bundle_id
        self.ignore_embedded_relationships = ignore_embedded_relationships
        self.ignore_embedded_relationships_smo = ignore_embedded_relationships_smo
        self.ignore_embedded_relationships_sro = ignore_embedded_relationships_sro
        self.object_key_mapping = {}
        if create_collection:
            self.create_s2a_indexes()
            if not skip_default_indexes:
                self.create_default_indexes()
            if create_taxii_views:
                self.create_taxii_views()

        if self.file:
            self.filename = Path(self.file).name

    def alter_objects(self, objects: list[dict]):
        for obj in objects:
            obj.update(self.arangodb_extra_data)
            for fn in self.alter_functions:
                try:
                    fn(obj)
                except Exception as e:
                    logging.warning(f"alter function {fn} failed on {obj}")
                    logging.warning(f"alter function {fn} failed on {obj}", exc_info=True)

    def add_object_alter_fn(self, modify_fn):
        if not callable(modify_fn):
            raise ValueError("Bad modification function passed")
        self.alter_functions.append(modify_fn)

    def create_s2a_indexes(self):
        for name, collection in self.arango.collections.items():
            collection.add_index(
                dict(
                    type="persistent",
                    name="s2a_search",
                    sparse=False,
                    fields=[
                        "id",
                        "modified",
                        "_is_latest",
                    ],
                    inBackground=True,
                    storedValues=["_record_modified", "_key", "_id"],
                )
            )

            collection.add_index(
                dict(
                    type="persistent",
                    name="s2a_unique_constraint",
                    unique=True,
                    fields=[
                        "id",
                        "_record_md5_hash",
                    ],
                    inBackground=True,
                )
            )
            if name.endswith("_edge_collection"):
                collection.add_index(
                    dict(
                        type="persistent",
                        name="s2a_search_edge",
                        sparse=True,
                        fields=[
                            "_from",
                            "_is_latest",
                        ],
                        inBackground=True,
                        storedValues=["_id"],
                    )
                )

    def create_taxii_views(self):
        views = set()
        for name, collection in self.arango.collections.items():
            collection.add_index(
                dict(
                    type="inverted",
                    name="taxii_search",
                    sparse=True,
                    fields=[
                        "_record_created",
                        "modified",
                        "id",
                        "_taxii.visible",
                        "_taxii.last",
                        "_taxii.first",
                        "spec_version",
                        "type",
                    ],
                    inBackground=True,
                    storedValues=["_key", "_created"],
                    primarySort={
                        "fields": [{"field": "_record_created", "direction": "asc"}]
                    },
                )
            )
            views.add('ats__' + name.removesuffix('_vertex_collection').removesuffix('_edge_collection'))

    def create_default_indexes(self):
        for name, collection in self.arango.collections.items():
            module_logger.info(
                f"creating indexes for collection {collection.db_name}/{name}"
            )
            time = int(datetime.now().timestamp())

            collection.add_index(
                dict(
                    type="persistent",
                    fields=["id"],
                    storedValues=[
                        "modified",
                        "created",
                        "type",
                        "_record_modified",
                        "spec_version",
                        "_record_md5_hash",
                    ],
                    inBackground=True,
                    name=f"by_stix_id_{time}",
                )
            )
            collection.add_index(
                dict(
                    type="persistent",
                    fields=["id", "type"],
                    storedValues=[
                        "modified",
                        "created",
                        "_record_modified",
                        "spec_version",
                        "_record_md5_hash",
                    ],
                    inBackground=True,
                    name=f"by_stix_id_type_{time}",
                )
            )
            collection.add_index(
                dict(
                    type="persistent",
                    fields=["modified", "created"],
                    storedValues=[
                        "type",
                        "_record_modified",
                        "id",
                        "spec_version",
                        "_record_md5_hash",
                    ],
                    inBackground=True,
                    name=f"by_stix_version_{time}",
                )
            )
            collection.add_index(
                dict(
                    type="persistent",
                    fields=["type"],
                    storedValues=[
                        "modified",
                        "created",
                        "_record_modified",
                        "id",
                        "spec_version",
                        "_record_md5_hash",
                    ],
                    inBackground=True,
                    name=f"by_stix_type_{time}",
                )
            )
            collection.add_index(
                dict(
                    type="persistent",
                    fields=["_record_modified", "_record_created"],
                    storedValues=[
                        "modified",
                        "created",
                        "type",
                        "id",
                        "spec_version",
                        "_record_md5_hash",
                    ],
                    inBackground=True,
                    name=f"by_insertion_time_{time}",
                )
            )
            if name.endswith("_edge_collection"):
                collection.add_index(
                    dict(
                        type="persistent",
                        fields=["source_ref", "target_ref", "relationship_type"],
                        storedValues=[
                            "modified",
                            "created",
                            "type",
                            "_record_modified",
                            "spec_version",
                            "_record_md5_hash",
                            "id",
                        ],
                        inBackground=True,
                        name=f"relation_from_{time}",
                    )
                )
                collection.add_index(
                    dict(
                        type="persistent",
                        fields=["target_ref", "source_ref", "relationship_type"],
                        storedValues=[
                            "modified",
                            "created",
                            "type",
                            "_record_modified",
                            "spec_version",
                            "_record_md5_hash",
                            "id",
                        ],
                        inBackground=True,
                        name=f"relation_to_{time}",
                    )
                )
                collection.add_index(
                    dict(
                        type="persistent",
                        fields=["relationship_type", "target_ref", "source_ref"],
                        storedValues=[
                            "modified",
                            "created",
                            "type",
                            "_record_modified",
                            "spec_version",
                            "_record_md5_hash",
                            "id",
                        ],
                        inBackground=True,
                        name=f"relation_type_{time}",
                    )
                )

    def default_objects(self):
        object_list = self.default_ref_objects
        for obj in json.loads(
            pkgutil.get_data("stix2arango", "templates/marking-definition.json")
        ):
            object_list.append(obj)
        return object_list

    def process_bundle_into_graph(
        self, objects_in, notes=None, is_default_objects=False
    ):
        module_logger.info(f"Reading vertex from file {self.file} now")

        objects = []
        insert_data = []  # That would be the overall statement
        for obj in tqdm(objects_in, desc="upload_vertices"):
            if obj.get("type") == "relationship":
                continue
            obj.setdefault("_stix2arango_note", notes or self.note)
            obj["_record_md5_hash"] = utils.generate_md5(obj)
            if not is_default_objects:
                obj["_bundle_id"] = self.bundle_id or ""
                obj["_file_name"] = self.filename or ""
                obj.update(self.arangodb_extra_data)
            objects.append(obj)
            insert_data.append(
                [obj.get("type"), obj.get("id"), True if "modified" in obj else False]
            )

        module_logger.info(
            f"Inserting objects into database. Total objects: {len(objects)}"
        )
        with self.arango.transactional(exclusive=[self.core_collection_edge, self.core_collection_vertex]):
            inserted_object_ids, existing_objects = (
                self.arango.insert_several_objects_chunked(
                    objects, self.core_collection_vertex
                )
            )
            deprecated_key_ids = self.arango.update_is_latest_several_chunked(
                inserted_object_ids, self.core_collection_vertex, self.core_collection_edge
            )

        self.update_object_key_mapping(self.core_collection_vertex, objects, existing_objects)
        return inserted_object_ids, existing_objects, deprecated_key_ids

    def update_object_key_mapping(self, collection, objects, existing_objects={}):
        for obj in objects:
            if db_key := existing_objects.get(f"{obj['id']};{obj['_record_md5_hash']}"):
                self.object_key_mapping[obj["id"]] = db_key
            else:
                self.object_key_mapping[obj["id"]] = "{collection}/{_key}".format(
                    collection=collection,
                    _key=obj.get("_key", "not_imported"),
                )

    def map_relationships(self, filename, objects_in):

        module_logger.info("Mapping Prebuilt Relationship Objects -> ")
        objects = []
        inserted_data = []
        obj: dict
        for obj in tqdm(objects_in, desc="upload_edges"):
            if obj.get("type") == "relationship":

                source_ref = obj.get("source_ref")
                target_ref = obj.get("target_ref")

                obj.setdefault("_from", f"{self.core_collection_vertex}/{source_ref}")
                obj.setdefault("_to", f"{self.core_collection_vertex}/{target_ref}")
                obj["_bundle_id"] = self.bundle_id or ""
                obj["_file_name"] = filename
                obj.setdefault("_is_ref", False)
                obj.setdefault("_stix2arango_note", self.note)
                # obj['_record_md5_hash'] = utils.generate_md5(obj)
                obj.update(self.arangodb_extra_data)
                objects.append(obj)
                inserted_data.append(
                    [
                        obj.get("type"),
                        obj.get("id"),
                        True if "modified" in obj else False,
                    ]
                )

        module_logger.info(
            f"Inserting relationship into database. Total objects: {len(objects)}"
        )
        with self.arango.transactional(exclusive=[self.core_collection_edge, self.core_collection_vertex]):
            inserted_object_ids, existing_objects = (
                self.arango.insert_relationships_chunked(
                    objects, self.object_key_mapping, self.core_collection_edge
                )
            )
            deprecated_key_ids = self.arango.update_is_latest_several_chunked(
                inserted_object_ids, self.core_collection_edge, self.core_collection_edge
            )
        self.update_object_key_mapping(self.core_collection_edge, objects, existing_objects)
        return inserted_object_ids, deprecated_key_ids

    def map_embedded_relationships(self, bundle_objects, inserted_object_ids):
        objects = []
        inserted_data = []
        for obj in tqdm(bundle_objects, desc="upload_embedded_edges"):
            if obj["id"] not in inserted_object_ids:
                continue
            if (
                self.ignore_embedded_relationships_smo and obj["type"] in SMO_TYPES
            ) or (
                self.ignore_embedded_relationships_sro and obj["type"] == "relationship"
            ):
                continue

            for ref_type, targets in utils.get_embedded_refs(obj):
                utils.create_relationship_obj(
                    obj=obj,
                    source=obj.get("id"),
                    targets=targets,
                    relationship=ref_type,
                    arango_obj=self,
                    bundle_id=self.bundle_id or '',
                    insert_statement=objects,
                    extra_data=self.arangodb_extra_data,
                )

        module_logger.info(
            f"Inserting embedded relationship into database. Total objects: {len(objects)}"
        )

        self.alter_objects(objects)
        with self.arango.transactional(exclusive=[self.core_collection_edge, self.core_collection_vertex]):
            inserted_object_ids, existing_objects = (
                self.arango.insert_relationships_chunked(
                    objects, self.object_key_mapping, self.core_collection_edge
                )
            )
            self.arango.update_is_latest_several_chunked(
                inserted_object_ids, self.core_collection_edge, self.core_collection_edge
            )
        return inserted_object_ids, existing_objects

    def import_default_objects(self):
        self.process_bundle_into_graph(
            self.default_objects(),
            notes="automatically imported on collection creation",
            is_default_objects=True,
        )

    def run(self, data=None):
        if not data and not self.file:
            raise Exception("file or data must be passed")

        if not data:
            if self.is_large_file:
                module_logger.info("using large file mode")
                os.makedirs("db_loader_tempfiles", exist_ok=True)
                bundle_loader = BundleLoader(
                    self.file, db_path=f"db_loader_tempfiles/mydb_{time.time()}.sqlite"
                )
                for chunk in bundle_loader.chunks:
                    self.run_with_bundle(
                        {
                            "type": "bundle",
                            "objects": chunk,
                            "id": bundle_loader.bundle_id,
                        }
                    )
                return
            else:
                module_logger.info("using regular file mode")
                with open(self.file, "r") as input_file:
                    file_data = input_file.read()
                    try:
                        data = json.loads(file_data)
                        self.bundle_id = self.bundle_id or data["id"]
                    except Exception as e:
                        raise Exception("Invalid file type")
                try:
                    validate(instance=data, schema=config.json_schema)
                except Exception as e:
                    raise Exception("Invalid File structure")

        self.run_with_bundle(data)

    def run_with_bundle(self, bundle_dict):
        if bundle_dict.get("type", None) != "bundle":
            raise Exception("Provided file is not a STIX bundle. Aborted")

        all_objects = bundle_dict["objects"]
        self.alter_objects(all_objects)

        module_logger.info(
            f"Loading default objects from url and store into {self.core_collection_vertex}"
        )
        self.import_default_objects()

        module_logger.info(
            f"Load objects from file: {self.file} and store into {self.core_collection_vertex}"
        )
        inserted_object_ids, _, deprecated_key_ids1 = self.process_bundle_into_graph(
            all_objects
        )
        module_logger.info("Mapping relationships now -> ")
        inserted_relationship_ids, deprecated_key_ids2 = self.map_relationships(
            self.filename, all_objects
        )

        if not self.ignore_embedded_relationships:
            module_logger.info(
                "Creating new embedded relationships using _refs and _ref"
            )
            self.map_embedded_relationships(
                all_objects, inserted_object_ids + inserted_relationship_ids
            )

        
        with self.arango.transactional(exclusive=[self.core_collection_edge, self.core_collection_vertex]):
            self.arango.deprecate_relationships(
                deprecated_key_ids1, self.core_collection_edge
            )
            self.arango.deprecate_relationships(
                deprecated_key_ids2, self.core_collection_edge
            )
