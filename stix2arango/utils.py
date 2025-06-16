from contextlib import contextmanager
from functools import lru_cache
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
from arango.database import StandardDatabase


EMBEDDED_RELATIONSHIP_RE = re.compile(r"([a-z\-_]+)[_\-]refs{0,1}")


@lru_cache
def load_file_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error loading JSON from {url}: {e}") from e


def create_relationship_obj(
    obj: dict,
    source: str,
    targets: list,
    relationship: str,
    insert_statement,
    bundle_id: str,
    arango_obj=None,
    extra_data=None,
):
    insert_data = []
    if not isinstance(targets, list):
        return []
    for target in targets:
        relationship_object = {
            "relationship_type": relationship,
        }
        for key in ["created", "modified", "object_marking_refs"]:
            if key in obj:
                relationship_object[key] = obj[key]

        relationship_object.update(
            id="relationship--"
            + str(
                uuid.uuid5(
                    config.namespace,
                    "{}+{}+{}".format(relationship, source, target),
                )
            ),
            created_by_ref=arango_obj.identity_ref["id"],
        )

        if not isinstance(target, str):
            continue
        relationship_object["source_ref"] = source
        relationship_object["target_ref"] = target
        relationship_object["_from"] = f"{arango_obj.core_collection_vertex}/{source}"
        relationship_object["_to"] = f"{arango_obj.core_collection_vertex}/{target}"
        relationship_object["_bundle_id"] = bundle_id
        relationship_object["_file_name"] = os.path.basename(arango_obj.file or "")
        relationship_object["_stix2arango_note"] = arango_obj.note
        relationship_object["_record_created"] = datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        relationship_object["_record_modified"] = relationship_object["_record_created"]
        relationship_object["_is_ref"] = True
        relationship_object["type"] = "relationship"
        relationship_object["spec_version"] = "2.1"
        # relationship_object['_record_md5_hash'] = generate_md5(relationship_object)
        if extra_data:
            relationship_object.update(extra_data)

        insert_statement.append(relationship_object)
        insert_data.append(
            [
                "relationship",
                relationship_object["id"],
                True if "modified" in obj else False,
            ]
        )
    return insert_data


def generate_md5(obj: dict):
    obj_copy = {k: v for k, v in obj.items() if not k.startswith("_")}
    for k in ["_from", "_to", "_stix2arango_note"]:
        if v := obj.get(k):
            obj_copy[k] = v
    json_str = json.dumps(obj_copy, sort_keys=True, default=str).encode("utf-8")
    return hashlib.md5(json_str).hexdigest()


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
        md5hash = object.get("_record_md5_hash")
        if not md5hash:
            md5hash = generate_md5(object)
        key = "{id}/{hash}".format(id=object["id"], hash=md5hash)
        objects_hashmap[key] = object
    return list(objects_hashmap.values())


def get_embedded_refs(object: list | dict, xpath: list = []):
    embedded_refs = []
    if isinstance(object, dict):
        for key, value in object.items():
            if key in ["source_ref", "target_ref"]:
                continue
            if match := EMBEDDED_RELATIONSHIP_RE.fullmatch(key):
                relationship_type = "-".join(xpath + match.group(1).split("_"))
                targets = value if isinstance(value, list) else [value]
                embedded_refs.append((relationship_type, targets))
            elif isinstance(value, list):
                embedded_refs.extend(get_embedded_refs(value, xpath + [key]))
    elif isinstance(object, list):
        for obj in object:
            if isinstance(obj, dict):
                embedded_refs.extend(get_embedded_refs(obj, xpath))
    return embedded_refs
