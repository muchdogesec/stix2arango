# python3 -m unittest tests/test_09-duplicate-objects-but-diff-times-in-bundle.py

import unittest
from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test09"
        cls.FILES = [
            dict(file="duplicate-objects-properties-different.json", ignore_embedded_relationships=False, stix2arango_note="test09"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test09_vertex_collection
                FILTER doc._is_latest == true
                AND doc._stix2arango_note != "automatically imported on collection creation"
                    RETURN doc
        )
        """
        expected_result = [2]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

    def test_query_2(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test09_vertex_collection
                FILTER doc._is_latest == false
                AND doc._stix2arango_note != "automatically imported on collection creation"
                    RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

    def test_query_3(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test09_edge_collection
                FILTER doc._is_latest == true
                AND doc._is_ref == false
                AND doc._stix2arango_note != "automatically imported on collection creation"
                    RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

    def test_query_4(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test09_edge_collection
                FILTER doc._is_latest == false
                AND doc._is_ref == false
                AND doc._stix2arango_note != "automatically imported on collection creation"
                    RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

    def test_query_5(self):
        query = """
        FOR doc IN test09_vertex_collection
            FILTER doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
            SORT doc.modified DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                modified: doc.modified
            }
        """
        expected_result = [
              {
                "id": "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd",
                "_is_latest": True,
                "modified": "2024-01-01T00:00:00.000Z"
              },
              {
                "id": "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd",
                "_is_latest": False,
                "modified": "2020-10-16T00:00:00.000Z"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

    def test_query_6(self):
        query = """
        FOR doc IN test09_vertex_collection
            FILTER doc.id == "software--50fa0834-9c63-5b0f-bf0e-dce02183253a"
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
            }
        """
        expected_result = [
              {
                "id": "software--50fa0834-9c63-5b0f-bf0e-dce02183253a",
                "_is_latest": True
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

if __name__ == '__main__':
    unittest.main()
