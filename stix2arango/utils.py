import requests
import logging
import uuid
import json
import hashlib
import os
from . import config
from datetime import datetime
module_logger = logging.getLogger("data_ingestion_service")


def load_file_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error loading JSON from {url}: {e}")
        return None


def verify_duplication(obj, object_list):

    if isinstance(object_list, list) and isinstance(obj, dict):
        match_string = f'"_key": "{obj.get("_key")}",'
        filtered_list = [obj_ for obj_ in object_list if match_string in obj_ ]
        if len(filtered_list)>0:
            return True
    return False


def get_object_details(obj, arango_obj):
    filters = f"doc.id=='{obj['id']}'"
    filters_dates = arango_obj.arango.execute_raw_query(
        query=f"for doc in {arango_obj.core_collection_edge} "
              f"filter {filters} limit 1 sort doc.created desc return "
              f"doc.created"
    )
    return filters_dates[0] if len(filters_dates)>0 else obj.get("modified")

def create_relationship_obj(
        obj:dict, source:str, targets:list, relationship:str, insert_statement,
        bundle_id:str, arango_obj =None):
    insert_data = []
    if isinstance(targets, list) and targets:
        for target in targets:
            if target:
                objects_= {
                    "created_by_ref": arango_obj.identity_ref.get("id"),
                    "relationship_type": relationship,
                    "created": obj.get("created"),
                    "modified": obj.get("modified"),
                    "object_marking_refs": obj.get("object_marking_refs")
                }
                objects_["id"] = "relationship--" + str(
                    uuid.uuid5(
                        config.namespace,
                        "{}+{}+{}".format(
                            relationship, source, target
                        ),
                    )
                )
                objects_["source_ref"] = f"{source}"
                objects_["target_ref"] = f"{target}"
                objects_["_from"] = f"{arango_obj.core_collection_vertex}/{source}"
                objects_["_to"] = f"{arango_obj.core_collection_vertex}/{target}"
                objects_['_bundle_id'] = bundle_id
                objects_['_file_name'] = os.path.basename(arango_obj.file)  if len(arango_obj.file.split("/")) > 1 else ""
                objects_['_stix2arango_note'] = arango_obj.note
                objects_['_record_created'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
                objects_['_record_modified'] = objects_['_record_created']
                objects_['_is_ref'] = True
                objects_['type'] = "relationship"
                objects_['spec_version'] = "2.1"
                objects_['_record_md5_hash'] = generate_md5(objects_)

                insert_statement.append(objects_)
                insert_data.append(
                    ["relationship", objects_["id"], True if "modified" in obj else False]
                )

        return insert_data


def generate_md5(obj:dict):
    obj_copy = {k: v for k, v in obj.items() if not k.startswith("_")}
    obj_copy["_stix2arango_note"] = obj.get("_stix2arango_note")
    json_str = json.dumps(obj_copy, sort_keys=True).encode('utf-8')
    return hashlib.md5(json_str).hexdigest()


def read_file_data(filename:str):
    with open(filename, "r") as input_file:
        file_data = input_file.read()
        try:
            data = json.loads(file_data)
        except Exception as e:
            raise Exception("Invalid file type")
    return data


def get_vertex_and_edge_collection_names(name):
        ENDINGS = ["vertex_collection", "edge_collection"]
        splits = name.split("_")
        if "_".join(splits[-2:]) in ENDINGS:
            splits = splits[:-2]
        return "_".join(splits + [ENDINGS[0]]), "_".join(splits + [ENDINGS[1]])