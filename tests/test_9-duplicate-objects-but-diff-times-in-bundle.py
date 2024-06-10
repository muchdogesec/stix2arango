# python3 -m unittest tests/test_9-duplicate-objects-but-diff-times-in-bundle.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test9"
        cls.STIX2ARANGO_NOTE_1 = "test9"
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "duplicate-objects-properties-different.json"
        cls.TEST_FILE_2 = ""
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN {
            vertices: LENGTH(
                FOR doc IN test9_vertex_collection
                    FILTER doc._is_latest == true
                    AND doc._stix2arango_note != "automatically imported on collection creation"
                        RETURN doc
                ),
            edges: LENGTH(
                FOR doc IN test9_edge_collection
                    FILTER doc._is_latest == true AND doc._is_ref == false
                    AND doc._stix2arango_note != "automatically imported on collection creation"
                        RETURN doc
                )
        }
        """
        expected_result = [{"vertices": 2, "edges": 1}]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # expect only one version of each object to be created software, indicator, and relationship

    def test_query_2(self):
        query = """
        RETURN {
            vertices: LENGTH(
                FOR doc IN test9_vertex_collection
                    FILTER doc._is_latest == false
                    AND doc._stix2arango_note != "automatically imported on collection creation"
                        RETURN doc
                ),
            edges: LENGTH(
                FOR doc IN test9_edge_collection
                    FILTER doc._is_latest == false AND doc._is_ref == false
                    AND doc._stix2arango_note != "automatically imported on collection creation"
                        RETURN doc
            )
        }
        """
        expected_result = [{"vertices": 1, "edges": 1}]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # indicator and relationship should have old versions

    def test_query_3(self):
        query = """
        FOR doc IN test9_vertex_collection
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

        # the versions of the indicator

    def test_query_4(self):
        query = """
        FOR doc IN test9_vertex_collection
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

        # only one version should be imported

if __name__ == '__main__':
    unittest.main()