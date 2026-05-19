import pytest
from stix2arango import config
from stix2arango.services.arangodb_service import ArangoDBService, VersionlessArangoDBService
from stix2arango.stix2arango.stix2arango import Stix2Arango
import arango.exceptions
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import re


def test_get_db_name():
    assert ArangoDBService.get_db_name("test") == 'test_database'
    assert ArangoDBService.get_db_name("test_database") == 'test_database'

@pytest.fixture(scope='module')
def service():
    s = ArangoDBService('test_s2a_arango_service', [], [], host_url=Stix2Arango.ARANGODB_URL, username=config.ARANGODB_USERNAME, password=config.ARANGODB_PASSWORD, create_db=True)
    yield s
    s.sys_db.delete_database('test_s2a_arango_service_database')


def test_init_creates_graph(service):
    assert service.db.has_graph('test_s2a_arango_service_graph')


def test_create_db(service):
    service.create_database('test_s2a_arango_service2')
    assert service.sys_db.has_database('test_s2a_arango_service2')
    service.create_database('test_s2a_arango_service2')
    service.sys_db.delete_database('test_s2a_arango_service2')

def test_create_collection(service):
    assert service.create_collection('ss_vertex_collection').info()['name'] == 'ss_vertex_collection', "created collection must have the passed name"
    assert service.create_collection('ss_vertex_collection').info()['name'] == 'ss_vertex_collection', "recreating should not throw error"

def test_execute_raw_query(service):
    c = service.create_collection('execute_raw_query')
    c.insert_many([{"a": 1}, {"a": 2}, {"a": 3}])
    assert service.execute_raw_query("FOR d IN @@collection FILTER d.a >= 2 RETURN d.a", bind_vars={'@collection': c.name}) == [2, 3]
    with pytest.raises(arango.exceptions.AQLQueryExecuteError):
        service.execute_raw_query("FOR d IN @@collection FILTER d.a >= 2 RETURN d.a")

def test_fix_edge_ref():
    assert ArangoDBService.fix_edge_ref('nothing') == "missing_collection/nothing"
    assert ArangoDBService.fix_edge_ref('abcd/nothing') == "abcd/nothing"

def test_transactional_resets_db(service):
    db = service.db
    with patch('arango.database.TransactionDatabase.commit_transaction') as mock_commit, service.transactional():
        pass
    assert service.db == db, "db not reset to original after context exit"
    mock_commit.assert_called_once()


def test_transactional_resets_db__on_failure(service):
    db = service.db
    with patch('arango.database.TransactionDatabase.abort_transaction') as mock_abort, pytest.raises(Exception), service.transactional():
        raise Exception("must raise")
    assert service.db == db, "db not reset to original after context exit"
    mock_abort.assert_called_once()


def test_insert_several_objects(service):
    col_name = 'test_insert_several'
    service.create_collection(col_name)
    objs = [
        {'id': 'indicator--1', 'type': 'indicator', 'name': 'test1', '_record_md5_hash': 'hash1'},
        {'id': 'relationship--1', 'type': 'relationship', 'source_ref': 'indicator--1', 'target_ref': 'indicator--2', '_record_md5_hash': 'hash2'}
    ]
    ids, existing = service.insert_several_objects(objs, col_name)
    assert ids == ['indicator--1', 'relationship--1']
    assert existing == {}
    
    res = service.execute_raw_query(f"FOR d IN {col_name} FILTER d.type == 'relationship' RETURN d")
    assert len(res) == 1
    assert res[0]['_target_type'] == 'indicator'
    assert res[0]['_source_type'] == 'indicator'
    assert res[0]['_is_latest'] is False


def test_update_is_latest_several(service):
    col_name = 'test_update_latest'
    col = service.create_collection(col_name)
    col.add_index(dict(
        type="persistent", 
        name="s2a_search", 
        fields=["id", "modified", "_is_latest"], 
        storedValues=["_record_modified", "_key", "_id"]
    ))
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    objs = [
        {'id': 'ind--1', 'type': 'indicator', 'modified': '2023-01-01T00:00:00.000Z', '_record_modified': '2023-01-01T00:00:00.000Z', '_is_latest': False, '_key': 'k1', '_id': f'{col_name}/k1'},
        {'id': 'ind--1', 'type': 'indicator', 'modified': '2023-01-02T00:00:00.000Z', '_record_modified': '2023-01-02T00:00:00.000Z', '_is_latest': False, '_key': 'k2', '_id': f'{col_name}/k2'}
    ]
    service.db.collection(col_name).insert_many(objs)
    
    deprecated = service.update_is_latest_several(['ind--1'], col_name)
    
    res = service.execute_raw_query(f"FOR d IN {col_name} SORT d.modified DESC RETURN d")
    assert res[0]['_is_latest'] is True
    assert res[1]['_is_latest'] is False
    assert deprecated == []


def test_get_relationships_to_deprecate(service):
    v_col = 'test_v_dep'
    e_col = 'test_e_dep'
    service.create_collection(v_col)
    service.create_collection(e_col)
    service.db.collection(e_col).add_index(dict(
        type="persistent", 
        name="s2a_search_edge", 
        fields=["_from", "_is_latest"], 
        storedValues=["_id"]
    ))

    vid = f"{v_col}/v1"
    service.db.collection(e_col).insert({'_key': 'r1', '_from': vid, '_to': 'v/v2', '_is_latest': True})
    
    keys = service.get_relationships_to_deprecate([vid], e_col)
    # Includes original vertex key and found relationship key
    assert 'v1' in keys
    assert 'r1' not in keys, "should not include _to in deprecation"


@pytest.fixture(scope='module')
def versionless_service():
    db_name = 'test_versionless_service_database'
    s = VersionlessArangoDBService(db_name, [], [], host_url=Stix2Arango.ARANGODB_URL, username=config.ARANGODB_USERNAME, password=config.ARANGODB_PASSWORD, create_db=True)
    yield s
    s.sys_db.delete_database(db_name)


def test_versionless_overrides(versionless_service):
    assert versionless_service.deprecate_relationships([], 'any') == 0
    assert versionless_service.update_is_latest_several_chunked([], 'any') == []


def test_versionless_insert_behavior(versionless_service):
    col_name = 'test_vless_insert'
    col = versionless_service.create_collection(col_name)
    col.add_index(dict(
        type="persistent", 
        name="s2a_search", 
        fields=["id", "modified", "_is_latest"], 
        storedValues=["_record_modified", "_key", "_id"]
    ))

    objs = [{'id': 'ind--1', 'type': 'indicator', '_record_md5_hash': 'h1'}]
    ids, existing = versionless_service.insert_several_objects(objs, col_name)
    
    assert ids == ['ind--1']
    assert existing == {}
    
    res = versionless_service.execute_raw_query(f"FOR d IN {col_name} RETURN d")
    assert res[0]['_is_latest'] is True
    assert res[0]['_taxii']['visible'] is True

    # Test idempotency (same MD5)
    ids2, existing2 = versionless_service.insert_several_objects(objs, col_name)
    assert ids2 == []
    assert len(existing2) == 1
    assert 'ind--1;h1' in existing2

    # Test update (different MD5)
    objs_updated = [{'id': 'ind--1', 'type': 'indicator', '_record_md5_hash': 'h2'}]
    ids3, existing3 = versionless_service.insert_several_objects(objs_updated, col_name)
    assert ids3 == ['ind--1']
    assert existing3 == {}
    
    res2 = versionless_service.execute_raw_query(f"FOR d IN {col_name} RETURN d")
    assert len(res2) == 1 # Replaced due to overwrite_mode="replace-insert"
    assert res2[0]['_is_latest'] is True
    assert res2[0]['_taxii']['visible'] is True
    assert res2[0]['_record_md5_hash'] == 'h2', "_record_md5_hash should be updated"
    assert res2[0]['_key'] == res[0]['_key'], "_key should remain the same"
    assert res2[0]['_record_created'] == res[0]['_record_created'], "_record_modified should remain the same"
    assert res2[0]['_record_modified'] != res[0]['_record_modified'], "_record_modified should be updated"