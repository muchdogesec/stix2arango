import pytest
from stix2arango.services.version_annotator import annotate_versions


@pytest.mark.parametrize(
    "objects,expected_annotations,expected_deprecated",
    [
        # Test Case 1: Single object with no versions
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                }
            ],
            [
                {
                    "_key": "key1",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": True, "last": True},
                }
            ],
            [],
        ),
        # Test Case 1.1: Single object with no versions, _taxii is None
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": None,
                }
            ],
            [
                {
                    "_key": "key1",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": True, "last": True},
                }
            ],
            [],
        ),
        # Test Case 2: Two versions - simple case
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
                {
                    "id": "indicator--1",
                    "_key": "key2",
                    "_id": "collection/key2",
                    "modified": "2024-01-02T00:00:00.000Z",
                    "_record_modified": "2024-01-02T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
            ],
            [
                {
                    "_key": "key1",
                    "_is_latest": False,
                    "_taxii": {"visible": True, "first": True, "last": False},
                },
                {
                    "_key": "key2",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": False, "last": True},
                },
            ],
            [],
        ),
        # Test Case 3: Multiple objects with same modified, different _record_modified
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
                {
                    "id": "indicator--1",
                    "_key": "key2",
                    "_id": "collection/key2",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-02T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
            ],
            [
                # key1 has no changes (already correct), only key2 changes
                {
                    "_key": "key2",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": True, "last": True},
                },
            ],
            [],
        ),
        # Test Case 4: Object with None modified field
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": None,
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                }
            ],
            [
                {
                    "_key": "key1",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": True, "last": True},
                }
            ],
            [],
        ),
        # Test Case 5: Deprecation scenario - object was latest but now isn't
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": True, "last": True},
                },
                {
                    "id": "indicator--1",
                    "_key": "key2",
                    "_id": "collection/key2",
                    "modified": "2024-01-02T00:00:00.000Z",
                    "_record_modified": "2024-01-02T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
            ],
            [
                {
                    "_key": "key1",
                    "_is_latest": False,
                    "_taxii": {"visible": True, "first": True, "last": False},
                },
                {
                    "_key": "key2",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": False, "last": True},
                },
            ],
            ["collection/key1"],
        ),
        # Test Case 6: Multiple objects with different IDs
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
                {
                    "id": "indicator--2",
                    "_key": "key2",
                    "_id": "collection/key2",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
            ],
            [
                {
                    "_key": "key1",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": True, "last": True},
                },
                {
                    "_key": "key2",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": True, "last": True},
                },
            ],
            [],
        ),
        # Test Case 7: Complex scenario with multiple versions and modified groups
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
                {
                    "id": "indicator--1",
                    "_key": "key2",
                    "_id": "collection/key2",
                    "modified": "2024-01-02T00:00:00.000Z",
                    "_record_modified": "2024-01-02T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
                {
                    "id": "indicator--1",
                    "_key": "key3",
                    "_id": "collection/key3",
                    "modified": "2024-01-02T00:00:00.000Z",
                    "_record_modified": "2024-01-03T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
                {
                    "id": "indicator--1",
                    "_key": "key4",
                    "_id": "collection/key4",
                    "modified": "2024-01-03T00:00:00.000Z",
                    "_record_modified": "2024-01-03T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
            ],
            [
                # key1: changes from all False to visible+first
                {
                    "_key": "key1",
                    "_is_latest": False,
                    "_taxii": {"visible": True, "first": True, "last": False},
                },
                # key2: no changes (stays all False)
                # key3: changes from all False to visible
                {
                    "_key": "key3",
                    "_is_latest": False,
                    "_taxii": {"visible": True, "first": False, "last": False},
                },
                # key4: changes from all False to visible+last+_is_latest
                {
                    "_key": "key4",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": False, "last": True},
                },
            ],
            [],
        ),
        # Test Case 8: No changes needed (all annotations already correct)
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": True, "last": True},
                }
            ],
            [],
            [],
        ),
        # Test Case 9: Mixed None and valid modified fields
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": None,
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
                {
                    "id": "indicator--1",
                    "_key": "key2",
                    "_id": "collection/key2",
                    "modified": "2024-01-02T00:00:00.000Z",
                    "_record_modified": "2024-01-02T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
            ],
            [
                {
                    "_key": "key1",
                    "_is_latest": False,
                    "_taxii": {"visible": True, "first": False, "last": False},
                },
                {
                    "_key": "key2",
                    "_is_latest": True,
                    "_taxii": {"visible": True, "first": True, "last": True},
                },
            ],
            [],
        ),
    ],
    ids=[
        "single_object_no_versions",
        "single_object_no_versions_taxii_none",
        "two_versions_simple",
        "same_modified_different_record",
        "none_modified_field",
        "deprecation_scenario",
        "multiple_different_ids",
        "complex_multiple_versions",
        "no_changes_needed",
        "mixed_none_and_valid_modified",
    ],
)
def test_annotate_versions(objects, expected_annotations, expected_deprecated):
    """Test version annotation with various scenarios"""
    annotations, deprecated = annotate_versions(objects)

    # Sort both lists by _key for consistent comparison
    annotations_sorted = sorted(annotations, key=lambda x: x["_key"])
    expected_sorted = sorted(expected_annotations, key=lambda x: x["_key"])

    assert annotations_sorted == expected_sorted
    assert sorted(deprecated) == sorted(expected_deprecated)


def test_empty_input():
    """Test with empty input list"""
    annotations, deprecated = annotate_versions([])
    assert annotations == []
    assert deprecated == []


@pytest.mark.parametrize(
    "objects,expected_visible_count",
    [
        # One visible per modified value
        (
            [
                {
                    "id": "indicator--1",
                    "_key": "key1",
                    "_id": "collection/key1",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-01T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
                {
                    "id": "indicator--1",
                    "_key": "key2",
                    "_id": "collection/key2",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "_record_modified": "2024-01-02T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
                {
                    "id": "indicator--1",
                    "_key": "key3",
                    "_id": "collection/key3",
                    "modified": "2024-01-02T00:00:00.000Z",
                    "_record_modified": "2024-01-02T00:00:00.000Z",
                    "_is_latest": False,
                    "_taxii": {"visible": False, "first": False, "last": False},
                },
            ],
            2,  # key2 (max _record_modified for 2024-01-01) and key3
        ),
    ],
    ids=["taxii_visible_per_modified"],
)
def test_taxii_visibility(objects, expected_visible_count):
    """Test that TAXII visibility is correctly assigned"""
    annotations, _ = annotate_versions(objects)
    visible_count = sum(1 for ann in annotations if ann["_taxii"]["visible"])
    assert visible_count == expected_visible_count


def test_multiple_groups_independently_annotated():
    """Test that different object IDs are processed independently"""
    objects = [
        {
            "id": "indicator--1",
            "_key": "key1",
            "_id": "collection/key1",
            "modified": "2024-01-01T00:00:00.000Z",
            "_record_modified": "2024-01-01T00:00:00.000Z",
            "_is_latest": False,
            "_taxii": {"visible": False, "first": False, "last": False},
        },
        {
            "id": "indicator--2",
            "_key": "key2",
            "_id": "collection/key2",
            "modified": "2024-01-01T00:00:00.000Z",
            "_record_modified": "2024-01-01T00:00:00.000Z",
            "_is_latest": False,
            "_taxii": {"visible": False, "first": False, "last": False},
        },
    ]

    annotations, _ = annotate_versions(objects)

    # Both should be latest since they're different objects
    assert all(ann["_is_latest"] for ann in annotations)
    assert len(annotations) == 2
