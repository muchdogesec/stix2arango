"""Tests for pre-upload and post-upload hooks in Stix2Arango."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from stix2arango.stix2arango import Stix2Arango, pre_upload_hook, post_upload_hook


@pytest.fixture(autouse=True)
def clear_hooks():
    """Clear all hooks before and after each test."""
    Stix2Arango.clear_pre_upload_hooks()
    Stix2Arango.clear_post_upload_hooks()
    yield
    Stix2Arango.clear_pre_upload_hooks()
    Stix2Arango.clear_post_upload_hooks()


@pytest.fixture
def mock_arango_service():
    """Create a mock ArangoDB service."""
    with patch('stix2arango.stix2arango.stix2arango.ArangoDBService') as mock:
        service = MagicMock()
        service.collections = {
            'vertex_collection': MagicMock(),
            'edge_collection': MagicMock(),
        }
        mock.return_value = service
        yield service


@pytest.fixture
def stix2arango_instance(mock_arango_service):
    """Create a Stix2Arango instance for testing."""
    with patch('stix2arango.stix2arango.stix2arango.config') as mock_config:
        mock_config.ARANGODB_HOST = 'localhost'
        mock_config.ARANGODB_PORT = 8529
        mock_config.ARANGODB_USERNAME = 'test'
        mock_config.ARANGODB_PASSWORD = 'test'
        mock_config.STIX2ARANGO_IDENTITY = 'http://test.com/identity.json'
        
        with patch('stix2arango.stix2arango.stix2arango.utils.load_file_from_url') as mock_load:
            mock_load.return_value = {'id': 'identity--test', 'type': 'identity'}
            
            instance = Stix2Arango(
                database="test_db",
                collection="test_collection",
                file="test_file.json",
                create_collection=False
            )
            yield instance


class TestPreUploadHooks:
    """Tests for pre-upload hooks."""
    
    def test_register_pre_upload_hook(self):
        """Test registering a pre-upload hook."""
        def my_hook(instance, collection_name, objects):
            pass
        
        Stix2Arango.register_pre_upload_hook(my_hook, fail_on_error=False)
        
        assert len(Stix2Arango._pre_upload_hooks) == 1
        assert Stix2Arango._pre_upload_hooks[0] == (my_hook, False)
    
    def test_register_pre_upload_hook_with_fail_on_error(self):
        """Test registering a pre-upload hook with fail_on_error=True."""
        def my_hook(instance, collection_name, objects):
            pass
        
        Stix2Arango.register_pre_upload_hook(my_hook, fail_on_error=True)
        
        assert len(Stix2Arango._pre_upload_hooks) == 1
        assert Stix2Arango._pre_upload_hooks[0] == (my_hook, True)
    
    def test_register_multiple_pre_upload_hooks(self):
        """Test registering multiple pre-upload hooks."""
        def hook1(instance, collection_name, objects):
            pass
        
        def hook2(instance, collection_name, objects):
            pass
        
        Stix2Arango.register_pre_upload_hook(hook1)
        Stix2Arango.register_pre_upload_hook(hook2)
        
        assert len(Stix2Arango._pre_upload_hooks) == 2
    
    def test_register_non_callable_pre_upload_hook_raises_error(self):
        """Test that registering a non-callable raises ValueError."""
        with pytest.raises(ValueError, match="Hook must be callable"):
            Stix2Arango.register_pre_upload_hook("not a function")
    
    def test_clear_pre_upload_hooks(self):
        """Test clearing all pre-upload hooks."""
        def my_hook(instance, collection_name, objects):
            pass
        
        Stix2Arango.register_pre_upload_hook(my_hook)
        assert len(Stix2Arango._pre_upload_hooks) == 1
        
        Stix2Arango.clear_pre_upload_hooks()
        assert len(Stix2Arango._pre_upload_hooks) == 0
    
    def test_pre_upload_hook_receives_correct_parameters(self, stix2arango_instance):
        """Test that pre-upload hook receives instance, collection_name, and objects."""
        hook_called = []
        
        def my_hook(instance, collection_name, objects):
            hook_called.append({
                'instance': instance,
                'collection_name': collection_name,
                'objects': objects
            })
        
        Stix2Arango.register_pre_upload_hook(my_hook)
        
        test_objects = [{'id': 'test-1', 'type': 'indicator'}]
        stix2arango_instance._run_pre_upload_hooks('test_collection', test_objects)
        
        assert len(hook_called) == 1
        assert hook_called[0]['instance'] == stix2arango_instance
        assert hook_called[0]['collection_name'] == 'test_collection'
        assert hook_called[0]['objects'] == test_objects
    
    def test_pre_upload_hook_modifies_objects(self, stix2arango_instance):
        """Test that pre-upload hook can modify objects in-place."""
        def add_field(instance, collection_name, objects):
            for obj in objects:
                obj['_custom_field'] = 'custom_value'
                obj['_collection'] = collection_name
        
        Stix2Arango.register_pre_upload_hook(add_field)
        
        test_objects = [
            {'id': 'test-1', 'type': 'indicator'},
            {'id': 'test-2', 'type': 'malware'}
        ]
        stix2arango_instance._run_pre_upload_hooks('vertex_collection', test_objects)
        
        assert all(obj['_custom_field'] == 'custom_value' for obj in test_objects)
        assert all(obj['_collection'] == 'vertex_collection' for obj in test_objects)
    
    def test_pre_upload_hooks_run_in_order(self, stix2arango_instance):
        """Test that multiple pre-upload hooks run in registration order."""
        execution_order = []
        
        def hook1(instance, collection_name, objects):
            execution_order.append('hook1')
            for obj in objects:
                obj['value'] = 1
        
        def hook2(instance, collection_name, objects):
            execution_order.append('hook2')
            for obj in objects:
                obj['value'] = obj.get('value', 0) + 10
        
        def hook3(instance, collection_name, objects):
            execution_order.append('hook3')
            for obj in objects:
                obj['value'] = obj.get('value', 0) + 100
        
        Stix2Arango.register_pre_upload_hook(hook1)
        Stix2Arango.register_pre_upload_hook(hook2)
        Stix2Arango.register_pre_upload_hook(hook3)
        
        test_objects = [{'id': 'test-1'}]
        stix2arango_instance._run_pre_upload_hooks('test_collection', test_objects)
        
        assert execution_order == ['hook1', 'hook2', 'hook3']
        assert test_objects[0]['value'] == 111  # 1 + 10 + 100
    
    def test_pre_upload_hook_exception_logged_when_fail_on_error_false(self, stix2arango_instance, caplog):
        """Test that hook exceptions are logged but don't stop processing when fail_on_error=False."""
        def failing_hook(instance, collection_name, objects):
            raise ValueError("Hook failed")
        
        def successful_hook(instance, collection_name, objects):
            for obj in objects:
                obj['success'] = True
        
        Stix2Arango.register_pre_upload_hook(failing_hook, fail_on_error=False)
        Stix2Arango.register_pre_upload_hook(successful_hook, fail_on_error=False)
        
        test_objects = [{'id': 'test-1'}]
        stix2arango_instance._run_pre_upload_hooks('test_collection', test_objects)
        
        # Second hook should still run
        assert test_objects[0]['success'] is True
        # Exception should be logged
        assert 'pre-upload hook' in caplog.text
        assert 'failed' in caplog.text
    
    def test_pre_upload_hook_exception_raises_when_fail_on_error_true(self, stix2arango_instance):
        """Test that hook exceptions stop processing when fail_on_error=True."""
        def failing_hook(instance, collection_name, objects):
            raise ValueError("Critical hook failure")
        
        def should_not_run(instance, collection_name, objects):
            objects[0]['should_not_exist'] = True
        
        Stix2Arango.register_pre_upload_hook(failing_hook, fail_on_error=True)
        Stix2Arango.register_pre_upload_hook(should_not_run, fail_on_error=False)
        
        test_objects = [{'id': 'test-1'}]
        
        with pytest.raises(ValueError, match="Critical hook failure"):
            stix2arango_instance._run_pre_upload_hooks('test_collection', test_objects)
        
        # Second hook should not have run
        assert 'should_not_exist' not in test_objects[0]
    
    def test_pre_upload_hook_runs_on_entire_object_list(self, stix2arango_instance):
        """Test that pre-upload hook receives entire list, not individual objects."""
        hook_call_count = []
        
        def count_calls(instance, collection_name, objects):
            hook_call_count.append(len(objects))
        
        Stix2Arango.register_pre_upload_hook(count_calls)
        
        test_objects = [
            {'id': 'test-1'},
            {'id': 'test-2'},
            {'id': 'test-3'},
        ]
        stix2arango_instance._run_pre_upload_hooks('test_collection', test_objects)
        
        # Hook should be called once with all 3 objects
        assert len(hook_call_count) == 1
        assert hook_call_count[0] == 3


class TestPostUploadHooks:
    """Tests for post-upload hooks."""
    
    def test_register_post_upload_hook(self):
        """Test registering a post-upload hook."""
        def my_hook(instance, collection_name, objects, **kwargs):
            pass
        
        Stix2Arango.register_post_upload_hook(my_hook, fail_on_error=False)
        
        assert len(Stix2Arango._post_upload_hooks) == 1
        assert Stix2Arango._post_upload_hooks[0] == (my_hook, False)
    
    def test_register_post_upload_hook_with_fail_on_error(self):
        """Test registering a post-upload hook with fail_on_error=True."""
        def my_hook(instance, collection_name, objects, **kwargs):
            pass
        
        Stix2Arango.register_post_upload_hook(my_hook, fail_on_error=True)
        
        assert len(Stix2Arango._post_upload_hooks) == 1
        assert Stix2Arango._post_upload_hooks[0] == (my_hook, True)
    
    def test_register_multiple_post_upload_hooks(self):
        """Test registering multiple post-upload hooks."""
        def hook1(instance, collection_name, objects, **kwargs):
            pass
        
        def hook2(instance, collection_name, objects, **kwargs):
            pass
        
        Stix2Arango.register_post_upload_hook(hook1)
        Stix2Arango.register_post_upload_hook(hook2)
        
        assert len(Stix2Arango._post_upload_hooks) == 2
    
    def test_register_non_callable_post_upload_hook_raises_error(self):
        """Test that registering a non-callable raises ValueError."""
        with pytest.raises(ValueError, match="Hook must be callable"):
            Stix2Arango.register_post_upload_hook("not a function")
    
    def test_clear_post_upload_hooks(self):
        """Test clearing all post-upload hooks."""
        def my_hook(instance, collection_name, objects, **kwargs):
            pass
        
        Stix2Arango.register_post_upload_hook(my_hook)
        assert len(Stix2Arango._post_upload_hooks) == 1
        
        Stix2Arango.clear_post_upload_hooks()
        assert len(Stix2Arango._post_upload_hooks) == 0
    
    def test_post_upload_hook_receives_correct_parameters(self, stix2arango_instance):
        """Test that post-upload hook receives instance, collection_name, objects, and kwargs."""
        hook_called = []
        
        def my_hook(instance, collection_name, objects, **kwargs):
            hook_called.append({
                'instance': instance,
                'collection_name': collection_name,
                'objects': objects,
                'kwargs': kwargs
            })
        
        Stix2Arango.register_post_upload_hook(my_hook)
        
        test_objects = [{'id': 'test-1', 'type': 'indicator'}]
        inserted_ids = ['key1', 'key2']
        existing_objects = {'key3': {'id': 'test-3'}}
        
        stix2arango_instance._run_post_upload_hooks(
            'test_collection', 
            test_objects,
            inserted_ids,
            existing_objects
        )
        
        assert len(hook_called) == 1
        assert hook_called[0]['instance'] == stix2arango_instance
        assert hook_called[0]['collection_name'] == 'test_collection'
        assert hook_called[0]['objects'] == test_objects
        assert hook_called[0]['kwargs']['inserted_ids'] == inserted_ids
        assert hook_called[0]['kwargs']['existing_objects'] == existing_objects
    
    def test_post_upload_hook_can_access_inserted_ids(self, stix2arango_instance):
        """Test that post-upload hook can access inserted_ids from kwargs."""
        captured_data = {}
        
        def capture_ids(instance, collection_name, objects, **kwargs):
            captured_data['inserted_ids'] = kwargs.get('inserted_ids', [])
            captured_data['existing_objects'] = kwargs.get('existing_objects', {})
        
        Stix2Arango.register_post_upload_hook(capture_ids)
        
        test_objects = [{'id': 'test-1'}]
        inserted_ids = ['key1', 'key2', 'key3']
        existing_objects = {'key4': {'id': 'test-4'}}
        
        stix2arango_instance._run_post_upload_hooks(
            'test_collection',
            test_objects,
            inserted_ids,
            existing_objects
        )
        
        assert captured_data['inserted_ids'] == inserted_ids
        assert captured_data['existing_objects'] == existing_objects
    
    def test_post_upload_hooks_run_in_order(self, stix2arango_instance):
        """Test that multiple post-upload hooks run in registration order."""
        execution_order = []
        
        def hook1(instance, collection_name, objects, **kwargs):
            execution_order.append('hook1')
        
        def hook2(instance, collection_name, objects, **kwargs):
            execution_order.append('hook2')
        
        def hook3(instance, collection_name, objects, **kwargs):
            execution_order.append('hook3')
        
        Stix2Arango.register_post_upload_hook(hook1)
        Stix2Arango.register_post_upload_hook(hook2)
        Stix2Arango.register_post_upload_hook(hook3)
        
        stix2arango_instance._run_post_upload_hooks('test_collection', [], [], {})
        
        assert execution_order == ['hook1', 'hook2', 'hook3']
    
    def test_post_upload_hook_exception_logged_when_fail_on_error_false(self, stix2arango_instance, caplog):
        """Test that hook exceptions are logged but don't stop processing when fail_on_error=False."""
        hooks_run = []
        
        def failing_hook(instance, collection_name, objects, **kwargs):
            hooks_run.append('failing')
            raise ValueError("Hook failed")
        
        def successful_hook(instance, collection_name, objects, **kwargs):
            hooks_run.append('successful')
        
        Stix2Arango.register_post_upload_hook(failing_hook, fail_on_error=False)
        Stix2Arango.register_post_upload_hook(successful_hook, fail_on_error=False)
        
        stix2arango_instance._run_post_upload_hooks('test_collection', [], [], {})
        
        # Both hooks should run
        assert hooks_run == ['failing', 'successful']
        # Exception should be logged
        assert 'post-upload hook' in caplog.text
        assert 'failed' in caplog.text
    
    def test_post_upload_hook_exception_raises_when_fail_on_error_true(self, stix2arango_instance):
        """Test that hook exceptions stop processing when fail_on_error=True."""
        hooks_run = []
        
        def failing_hook(instance, collection_name, objects, **kwargs):
            hooks_run.append('failing')
            raise ValueError("Critical hook failure")
        
        def should_not_run(instance, collection_name, objects, **kwargs):
            hooks_run.append('should_not_run')
        
        Stix2Arango.register_post_upload_hook(failing_hook, fail_on_error=True)
        Stix2Arango.register_post_upload_hook(should_not_run, fail_on_error=False)
        
        with pytest.raises(ValueError, match="Critical hook failure"):
            stix2arango_instance._run_post_upload_hooks('test_collection', [], [], {})
        
        # Second hook should not have run
        assert hooks_run == ['failing']


class TestHookDecorators:
    """Tests for hook decorators."""
    
    def test_pre_upload_hook_decorator(self):
        """Test @pre_upload_hook decorator registers hook."""
        @pre_upload_hook()
        def my_hook(instance, collection_name, objects):
            pass
        
        assert len(Stix2Arango._pre_upload_hooks) == 1
        assert Stix2Arango._pre_upload_hooks[0][0] == my_hook
        assert Stix2Arango._pre_upload_hooks[0][1] is False
    
    def test_pre_upload_hook_decorator_with_fail_on_error(self):
        """Test @pre_upload_hook decorator with fail_on_error=True."""
        @pre_upload_hook(fail_on_error=True)
        def my_hook(instance, collection_name, objects):
            pass
        
        assert len(Stix2Arango._pre_upload_hooks) == 1
        assert Stix2Arango._pre_upload_hooks[0][0] == my_hook
        assert Stix2Arango._pre_upload_hooks[0][1] is True
    
    def test_post_upload_hook_decorator(self):
        """Test @post_upload_hook decorator registers hook."""
        @post_upload_hook()
        def my_hook(instance, collection_name, objects, **kwargs):
            pass
        
        assert len(Stix2Arango._post_upload_hooks) == 1
        assert Stix2Arango._post_upload_hooks[0][0] == my_hook
        assert Stix2Arango._post_upload_hooks[0][1] is False
    
    def test_post_upload_hook_decorator_with_fail_on_error(self):
        """Test @post_upload_hook decorator with fail_on_error=True."""
        @post_upload_hook(fail_on_error=True)
        def my_hook(instance, collection_name, objects, **kwargs):
            pass
        
        assert len(Stix2Arango._post_upload_hooks) == 1
        assert Stix2Arango._post_upload_hooks[0][0] == my_hook
        assert Stix2Arango._post_upload_hooks[0][1] is True
    
    def test_decorated_function_still_callable(self):
        """Test that decorated functions can still be called directly."""
        @pre_upload_hook()
        def my_pre_hook(instance, collection_name, objects):
            return "pre_result"
        
        @post_upload_hook()
        def my_post_hook(instance, collection_name, objects, **kwargs):
            return "post_result"
        
        # Functions should still be callable
        assert my_pre_hook(None, 'test', []) == "pre_result"
        assert my_post_hook(None, 'test', []) == "post_result"
    
    def test_multiple_decorators_can_be_used(self):
        """Test that multiple functions can be decorated."""
        @pre_upload_hook()
        def hook1(instance, collection_name, objects):
            pass
        
        @pre_upload_hook(fail_on_error=True)
        def hook2(instance, collection_name, objects):
            pass
        
        @post_upload_hook()
        def hook3(instance, collection_name, objects, **kwargs):
            pass
        
        assert len(Stix2Arango._pre_upload_hooks) == 2
        assert len(Stix2Arango._post_upload_hooks) == 1


class TestHookIntegration:
    """Integration tests for hooks with alter_objects."""
    
    def test_pre_upload_hook_runs_after_alter_objects(self, stix2arango_instance):
        """Test that pre-upload hooks run after instance-level alter functions."""
        execution_order = []
        
        def alter_fn(obj):
            execution_order.append('alter')
            obj['altered'] = True
        
        def pre_hook(instance, collection_name, objects):
            execution_order.append('pre_hook')
            for obj in objects:
                obj['pre_hooked'] = True
                # Verify alter_fn ran first
                assert obj.get('altered') is True
        
        stix2arango_instance.add_object_alter_fn(alter_fn)
        Stix2Arango.register_pre_upload_hook(pre_hook)
        
        test_objects = [{'id': 'test-1'}]
        stix2arango_instance._run_pre_upload_hooks('test_collection', test_objects)
        
        # Both should have run
        assert test_objects[0]['altered'] is True
        assert test_objects[0]['pre_hooked'] is True
        assert execution_order == ['alter', 'pre_hook']
    
    def test_hooks_work_with_different_collection_names(self, stix2arango_instance):
        """Test that hooks receive correct collection names for vertex and edge collections."""
        collection_names_received = []
        
        def track_collections(instance, collection_name, objects):
            collection_names_received.append(collection_name)
        
        Stix2Arango.register_pre_upload_hook(track_collections)
        
        stix2arango_instance._run_pre_upload_hooks('vertex_collection', [{'id': 'v1'}])
        stix2arango_instance._run_pre_upload_hooks('edge_collection', [{'id': 'e1'}])
        
        assert collection_names_received == ['vertex_collection', 'edge_collection']


class TestHookClassLevelBehavior:
    """Tests for class-level hook behavior across instances."""
    
    def test_hooks_are_shared_across_instances(self, mock_arango_service):
        """Test that hooks registered at class level affect all instances."""
        def my_hook(instance, collection_name, objects):
            for obj in objects:
                obj['shared_hook'] = True
        
        Stix2Arango.register_pre_upload_hook(my_hook)
        
        with patch('stix2arango.stix2arango.stix2arango.config') as mock_config:
            mock_config.ARANGODB_HOST = 'localhost'
            mock_config.ARANGODB_PORT = 8529
            mock_config.ARANGODB_USERNAME = 'test'
            mock_config.ARANGODB_PASSWORD = 'test'
            mock_config.STIX2ARANGO_IDENTITY = 'http://test.com/identity.json'
            
            with patch('stix2arango.stix2arango.stix2arango.utils.load_file_from_url') as mock_load:
                mock_load.return_value = {'id': 'identity--test', 'type': 'identity'}
                
                instance1 = Stix2Arango(database="db1", collection="col1", file="file1.json", create_collection=False)
                instance2 = Stix2Arango(database="db2", collection="col2", file="file2.json", create_collection=False)
                
                objects1 = [{'id': 'test-1'}]
                objects2 = [{'id': 'test-2'}]
                
                instance1._run_pre_upload_hooks('test', objects1)
                instance2._run_pre_upload_hooks('test', objects2)
                
                # Both should have been modified by the same hook
                assert objects1[0]['shared_hook'] is True
                assert objects2[0]['shared_hook'] is True
    
    def test_clearing_hooks_affects_all_instances(self, mock_arango_service):
        """Test that clearing hooks at class level affects all instances."""
        def my_hook(instance, collection_name, objects):
            pass
        
        Stix2Arango.register_pre_upload_hook(my_hook)
        
        with patch('stix2arango.stix2arango.stix2arango.config') as mock_config:
            mock_config.ARANGODB_HOST = 'localhost'
            mock_config.ARANGODB_PORT = 8529
            mock_config.ARANGODB_USERNAME = 'test'
            mock_config.ARANGODB_PASSWORD = 'test'
            mock_config.STIX2ARANGO_IDENTITY = 'http://test.com/identity.json'
            
            with patch('stix2arango.stix2arango.stix2arango.utils.load_file_from_url') as mock_load:
                mock_load.return_value = {'id': 'identity--test', 'type': 'identity'}
                
                instance1 = Stix2Arango(database="db1", collection="col1", file="file1.json", create_collection=False)
                instance2 = Stix2Arango(database="db2", collection="col2", file="file2.json", create_collection=False)
                
                assert len(instance1._pre_upload_hooks) == 1
                assert len(instance2._pre_upload_hooks) == 1
                
                Stix2Arango.clear_pre_upload_hooks()
                
                assert len(instance1._pre_upload_hooks) == 0
                assert len(instance2._pre_upload_hooks) == 0


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_pre_upload_hook_with_empty_objects_list(self, stix2arango_instance):
        """Test that hooks handle empty object lists gracefully."""
        hook_called = []
        
        def my_hook(instance, collection_name, objects):
            hook_called.append(len(objects))
        
        Stix2Arango.register_pre_upload_hook(my_hook)
        stix2arango_instance._run_pre_upload_hooks('test_collection', [])
        
        assert hook_called == [0]
    
    def test_post_upload_hook_with_empty_kwargs(self, stix2arango_instance):
        """Test that post-upload hooks can handle missing kwargs."""
        captured = {}
        
        def my_hook(instance, collection_name, objects, **kwargs):
            captured['inserted_ids'] = kwargs.get('inserted_ids', [])
            captured['existing_objects'] = kwargs.get('existing_objects', {})
            captured['unknown_key'] = kwargs.get('unknown_key', None)
        
        Stix2Arango.register_post_upload_hook(my_hook)
        stix2arango_instance._run_post_upload_hooks('test', [], [], {})
        
        assert captured['inserted_ids'] == []
        assert captured['existing_objects'] == {}
        assert captured['unknown_key'] is None
    
    def test_mixed_fail_on_error_settings(self, stix2arango_instance):
        """Test hooks with mixed fail_on_error settings."""
        execution_order = []
        
        def hook1(instance, collection_name, objects):
            execution_order.append('hook1')
        
        def hook2_fails(instance, collection_name, objects):
            execution_order.append('hook2_fails')
            raise ValueError("Hook2 error")
        
        def hook3(instance, collection_name, objects):
            execution_order.append('hook3')
        
        Stix2Arango.register_pre_upload_hook(hook1, fail_on_error=False)
        Stix2Arango.register_pre_upload_hook(hook2_fails, fail_on_error=False)
        Stix2Arango.register_pre_upload_hook(hook3, fail_on_error=True)
        
        # All hooks should run since hook2 doesn't fail the process
        stix2arango_instance._run_pre_upload_hooks('test', [{'id': 'test'}])
        
        assert execution_order == ['hook1', 'hook2_fails', 'hook3']
