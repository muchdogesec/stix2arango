# python3 -m unittest tests/test_08-duplicate-objects-in-bundle-all-identical.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test08"
        cls.STIX2ARANGO_NOTE_1 = "test08"
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "duplicate-objects-all-properties-same.json"
        cls.TEST_FILE_2 = ""
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test08_vertex_collection
                FILTER doc._is_latest == true
                AND doc._stix2arango_note != "automatically imported on collection creation"
                	RETURN doc
        )
        """
        expected_result = [2]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # expect only one version of each object to be created

    def test_query_2(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test08_vertex_collection
                FILTER doc._is_latest == false
                AND doc._stix2arango_note != "automatically imported on collection creation"
                	RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # expect no versions to be created as duplicate objects in bundle should be discarded

    def test_query_3(self):
        query = """
        FOR doc IN test08_vertex_collection
            FILTER doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
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
			    "modified": "2023-02-28T00:00:00.000Z"
			  }
			]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because the duplicate object should not exist

if __name__ == '__main__':
    unittest.main()