import re
import requests
import logging
import uuid
import json
import hashlib
import os
from . import config
from datetime import datetime
module_logger = logging.getLogger("data_ingestion_service")


EMBEDDED_RELATIONSHIP_RE = re.compile(r"([a-z\-_]+)[_\-]refs{0,1}")

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
    if not isinstance(targets, list):
        return []
    for target in targets:
        relationship_object= {
            "created_by_ref": arango_obj.identity_ref.get("id"),
            "relationship_type": relationship,
        }
        for key in ["created", "modified", "object_marking_refs"]:
            if key in obj:
                relationship_object[key] = obj[key]
        
        relationship_object["id"] = "relationship--" + str(
            uuid.uuid5(
                config.namespace,
                "{}+{}+{}".format(
                    relationship, source, target
                ),
            )
        )
        if not isinstance(target, str):
            continue
        relationship_object["source_ref"] = source
        relationship_object["target_ref"] = target
        relationship_object["_from"] = f"{arango_obj.core_collection_vertex}/{source}"
        relationship_object["_to"] = f"{arango_obj.core_collection_vertex}/{target}"
        relationship_object['_bundle_id'] = bundle_id
        relationship_object['_file_name'] = os.path.basename(arango_obj.file)  if len(arango_obj.file.split("/")) > 1 else ""
        relationship_object['_stix2arango_note'] = arango_obj.note
        relationship_object['_record_created'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        relationship_object['_record_modified'] = relationship_object['_record_created']
        relationship_object['_is_ref'] = True
        relationship_object['type'] = "relationship"
        relationship_object['spec_version'] = "2.1"
        relationship_object['_record_md5_hash'] = generate_md5(relationship_object)

        insert_statement.append(relationship_object)
        insert_data.append(
            ["relationship", relationship_object["id"], True if "modified" in obj else False]
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

def chunked(iterable, n):
    if not iterable:
        return []
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]


def remove_duplicates(objects):
    objects_hashmap = {}
    for object in objects:
        md5hash = object.get('_record_md5_hash')
        if not md5hash:
            md5hash = generate_md5(object)
        key = "{id}/{hash}".format(id=object['id'], hash=md5hash)
        objects_hashmap[key] = object
    return list(objects_hashmap.values())


def get_embedded_refs(object: list|dict, xpath: list = []):
    embedded_refs = []
    if isinstance(object, dict):
        for key, value in object.items():
            if key in ["source_ref", "target_ref"]:
                continue
            if match := EMBEDDED_RELATIONSHIP_RE.fullmatch(key):
                relationship_type = "-".join(xpath + match.group(1).split('_'))
                targets = value if isinstance(value, list) else [value]
                embedded_refs.append((relationship_type, targets))
            elif isinstance(value, list):
                embedded_refs.extend(get_embedded_refs(value, xpath + [key]))
    elif isinstance(object, list):
        for obj in object:
            if isinstance(obj, dict):
                embedded_refs.extend(get_embedded_refs(obj, xpath))
    return embedded_refs
