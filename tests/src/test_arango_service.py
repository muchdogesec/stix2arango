

import pytest
from stix2arango import config
from stix2arango.services.arangodb_service import ArangoDBService
from stix2arango.stix2arango.stix2arango import Stix2Arango
import arango.exceptions
from unittest.mock import patch, MagicMock


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

