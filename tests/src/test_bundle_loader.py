import json
import pytest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from stix2arango.stix2arango.bundle_loader import BundleLoader  # adjust this import path

# Sample bundle with related and unrelated objects
STIX_BUNDLE = {
    "type": "bundle",
    "id": "bundle--example",
    "objects": [
        {"id": "indicator--1", "type": "indicator"},
        {"id": "indicator--2", "type": "indicator"},
        {"id": "relationship--1", "type": "relationship", "source_ref": "indicator--1", "target_ref": "indicator--2"},
        {"id": "attack-pattern--3", "type": "attack-pattern"},
    ]
}

@pytest.fixture
def temp_json_file():
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as f:
        json.dump(STIX_BUNDLE, f)
        return f.name

def test_init_db_and_tempfile_creation():
    loader = BundleLoader(file_path=tempfile.mkstemp()[1])
    assert isinstance(loader.db_path, str)
    assert Path(loader.db_path).exists()

def test_save_to_sqlite_inserts_objects(temp_json_file):
    loader = BundleLoader(file_path=temp_json_file)
    objects = STIX_BUNDLE["objects"]
    loader.save_to_sqlite(objects)

    cursor = loader.conn.execute("SELECT COUNT(*) FROM objects")
    count = cursor.fetchone()[0]
    assert count == len(objects)

def test_build_groups_creates_correct_groups(temp_json_file):
    loader = BundleLoader(file_path=temp_json_file, chunk_size_min=1)
    groups = loader.build_groups()

    # There should be at least 2 groups: one for related indicators, one for attack-pattern
    assert isinstance(groups, list)
    flat = [id_ for group in groups for id_ in group]
    assert "indicator--1" in flat
    assert "indicator--2" in flat
    assert "relationship--1" in flat
    assert "attack-pattern--3" in flat

def test_load_objects_by_ids(temp_json_file):
    loader = BundleLoader(file_path=temp_json_file)
    loader.save_to_sqlite(STIX_BUNDLE["objects"])

    result = loader.load_objects_by_ids(["indicator--1", "attack-pattern--3"])
    assert isinstance(result, list)
    assert {obj["id"] for obj in result} == {"indicator--1", "attack-pattern--3"}

def test_get_objects_returns_objects(temp_json_file):
    loader = BundleLoader(file_path=temp_json_file)
    loader.save_to_sqlite(STIX_BUNDLE["objects"])

    result = loader.get_objects(["indicator--1"])
    assert isinstance(result, list)
    assert result[0]["id"] == "indicator--1"

def test_chunks_generator(temp_json_file):
    loader = BundleLoader(file_path=temp_json_file, chunk_size_min=1)
    chunks = list(loader.chunks)

    assert isinstance(chunks, list)
    for chunk in chunks:
        assert isinstance(chunk, list)
        assert all("id" in obj for obj in chunk)

def test_chunks_with_no_existing_groups_calls_build_groups(temp_json_file):
    loader = BundleLoader(file_path=temp_json_file, chunk_size_min=1)
    with patch.object(loader, 'build_groups', wraps=loader.build_groups) as mocked:
        chunks = list(loader.chunks)
        mocked.assert_called_once()
        assert len(chunks) > 0

def test_no_crash_on_missing_relationship_fields(temp_json_file):
    # Remove `source_ref` and `target_ref` to simulate bad data
    bad_bundle = {
        "type": "bundle",
        "objects": [{"id": "bad--1", "type": "relationship"}]
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(bad_bundle, f)
        path = f.name

    loader = BundleLoader(file_path=path)
    loader.build_groups()
    assert loader.groups  # It should still group the single object


def test_sqlite_file_removed_after_gc(temp_json_file):
    loader = BundleLoader(file_path=temp_json_file, chunk_size_min=1)
    db_path = Path(loader.db_path)
    assert db_path.exists()
    del loader
    assert not db_path.exists(), "should already be deleted"

