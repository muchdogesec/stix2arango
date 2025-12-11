from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
from stix2arango import utils
from stix2arango.config import DOGESEC_IDENTITY


def test_load_file_from_url():
    assert (
        utils.load_file_from_url(DOGESEC_IDENTITY)["id"]
        == "identity--9779a2db-f98c-5f4b-8d08-8ee04e02dbb5"
    )

    with pytest.raises(Exception):
        utils.load_file_from_url("https://gogle.cm/ojkskja")


def test_remove_duplicates():
    assert (
        len(
            utils.remove_duplicates(
                [
                    {
                        "id": "all-the-same",
                    },
                    {
                        "id": "all-the-same",
                    },
                    {"id": "all-the-same", "a": 1},
                    {"id": "all-the-same", "a": 1, "_is_latest": True},
                    {"id": "all-the-same", "a": 2, "b": 1},
                    {"id": "all-the-same", "a": 2, "b": 1, "c": 1},
                    {"id": "all-the-same", "a": 2, "b": 1, "c": 1, "_is": 8},
                ]
            )
        )
        == 4
    )


def test_get_embedded_refs():
    assert utils.get_embedded_refs(
        {
            "abc_ref": "ref1",
            "abcd_refs": ["ref1", "ref2"],
            "abcde": [{"abcdef_ref": "ref7"}, {"abcd_efgh_ref": "ref8"}],
        }
    ) == [
        ("abc", ["ref1"]),
        ("abcd", ["ref1", "ref2"]),
        ("abcde-abcdef", ["ref7"]),
        ("abcde-abcd-efgh", ["ref8"]),
    ]


def test_get_embedded_refs_empty():
    assert utils.get_embedded_refs(
        {
            "abc_ref": "ref1",
            "empty_ref": "",  # skipped entirely
            "some_empty_refs": ["ref10", "", "ref9"],  # empty ref skipped
            "abcd_refs": ["ref1", "ref2"],
            "abcde": [{"abcdef_ref": "ref7"}, {"abcd_efgh_ref": "ref8"}],
        }
    ) == [
        ("abc", ["ref1"]),
        ("some-empty", ["ref10", "ref9"]),
        ("abcd", ["ref1", "ref2"]),
        ("abcde-abcdef", ["ref7"]),
        ("abcde-abcd-efgh", ["ref8"]),
    ]


def test_get_embedded_refs__attributes_whitelist():
    assert utils.get_embedded_refs(
        {
            "abc_ref": "ref1",
            "abcd_refs": ["ref1", "ref2"],
            "abcde": [{"abcdef_ref": "ref7"}, {"abcd_efgh_ref": "ref8"}],
        },
        attributes=["abcd_efgh_ref", "abc_ref"],
    ) == [
        ("abc", ["ref1"]),
        (
            "abcde-abcd-efgh",
            ["ref8"],
        ),
    ]


def test_get_vertex_and_edge_collection_names():
    assert utils.get_vertex_and_edge_collection_names("ade") == (
        "ade_vertex_collection",
        "ade_edge_collection",
    )
    assert utils.get_vertex_and_edge_collection_names("ade_edge_collection") == (
        "ade_vertex_collection",
        "ade_edge_collection",
    )
    assert utils.get_vertex_and_edge_collection_names("ade_vertex_collection") == (
        "ade_vertex_collection",
        "ade_edge_collection",
    )


def test_create_relationship__no_targets():
    assert utils.create_relationship_obj(None, None, None, None, None, None) == []


def test_create_relationships():
    obj = {
        "created": "2024-01-01T00:00:00.000000",
        "modified": "2024-01-02T00:00:00.000000",
        "object_marking_refs": ["marking--xyz"],
    }

    source = "indicator--source"
    targets = ["malware--target1", "software--target--2"]
    relationship = "indicates"
    insert_statement = []
    bundle_id = "bundle--xyz"
    extra_data = {"confidence": 80, "labels": ["example"]}
    arango_obj = MagicMock()
    arango_obj.identity_ref = {"id": "identity--abcd"}
    arango_obj.core_collection_vertex = "vertices"
    arango_obj.file = "/some/path/file.txt"
    arango_obj.note = "This is a note"

    utils.create_relationship_obj(
        obj=obj,
        source=source,
        targets=targets,
        relationship=relationship,
        insert_statement=insert_statement,
        bundle_id=bundle_id,
        arango_obj=arango_obj,
        extra_data=extra_data,
    )

    assert len(insert_statement) == 2
    assert insert_statement == [
        {
            "relationship_type": "indicates",
            "created": "2024-01-01T00:00:00.000000",
            "modified": "2024-01-02T00:00:00.000000",
            "object_marking_refs": ["marking--xyz"],
            "id": "relationship--8a86537f-d4bb-55bc-b06d-ddeabbd9899d",
            "created_by_ref": "identity--abcd",
            "source_ref": "indicator--source",
            "target_ref": "malware--target1",
            "_from": "vertices/indicator--source",
            "_to": "vertices/malware--target1",
            "_bundle_id": "bundle--xyz",
            "_file_name": "file.txt",
            "_stix2arango_note": "This is a note",
            "_is_ref": True,
            "type": "relationship",
            "spec_version": "2.1",
            "external_references": [
                {
                    "source_name": "stix2arango",
                    "description": "embedded-relationship",
                }
            ],
            "confidence": 80,
            "labels": ["example"],
        },
        {
            "relationship_type": "indicates",
            "created": "2024-01-01T00:00:00.000000",
            "modified": "2024-01-02T00:00:00.000000",
            "object_marking_refs": ["marking--xyz"],
            "id": "relationship--fda071b0-e1e8-5831-a707-850f1b1a5a0e",
            "created_by_ref": "identity--abcd",
            "source_ref": "indicator--source",
            "target_ref": "software--target--2",
            "_from": "vertices/indicator--source",
            "_to": "vertices/software--target--2",
            "_bundle_id": "bundle--xyz",
            "_file_name": "file.txt",
            "_stix2arango_note": "This is a note",
            "_is_ref": True,
            "type": "relationship",
            "spec_version": "2.1",
            "external_references": [
                {
                    "source_name": "stix2arango",
                    "description": "embedded-relationship",
                }
            ],
            "confidence": 80,
            "labels": ["example"],
        },
    ]
