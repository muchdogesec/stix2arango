# python3 -m unittest tests/test_24-test-hidden-properties.py

import unittest
from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test24"
        cls.FILES = [
            dict(file="sigma-rule-bundle.json", ignore_embedded_relationships=False, stix2arango_note="test24"),
        ]

        
# test everything has custom hidden fields in vertex

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test24_vertex_collection
            FILTER doc._stix2arango_note != "automatically imported on collection creation"
              AND doc._stix2arango_note != null
              AND doc._record_modified != null 
              AND doc._record_created != null 
              AND doc._is_latest != null
              AND doc._record_md5_hash != null 
              AND doc._bundle_id != null
              AND doc._file_name != null
                RETURN doc
        )
        """
        expected_result = [3107]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

# should match test 1

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test24_vertex_collection
            FILTER doc._stix2arango_note != "automatically imported on collection creation"
                RETURN doc
        )
        """
        expected_result = [3107]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

# test everything has custom hidden fields in edge

    def test_query_3(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test24_edge_collection
            FILTER doc._stix2arango_note != null
              AND doc._record_modified != null 
              AND doc._record_created != null 
              AND doc._is_latest != null
              AND doc._record_md5_hash != null 
              AND doc._bundle_id != null 
              AND doc._file_name != null
              AND doc._stix2arango_ref_err != null
              AND doc._record_md5_hash != null 
              AND doc._file_name != null
              AND doc._target_type != null
              AND doc._source_type != null
                RETURN doc
        )
        """
        expected_result = [15946]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

# same as test 3

    def test_query_4(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test24_edge_collection
                RETURN doc
        )
        """
        expected_result = [15946]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

if __name__ == '__main__':
    unittest.main()