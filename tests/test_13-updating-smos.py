# python3 -m unittest tests/test_13-updating-smos.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test13"
        cls.STIX2ARANGO_NOTE_1 = "test13"
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "smo-original.json"
        cls.TEST_FILE_2 = "smo-updated.json"
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test13_vertex_collection
            FILTER doc._is_latest == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # number of objects in bundle

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test13_vertex_collection
            FILTER doc._is_latest == false
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # old version of object

    def test_query_3(self):
        query = """
        FOR doc IN test13_vertex_collection
            FILTER doc.id == "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41aa"
            SORT doc.doc._is_latest DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                name: doc.name
            }
        """
        expected_result = [
              {
                "id": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41aa",
                "_is_latest": False,
                "name": "original"
              },
              {
                "id": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41aa",
                "_is_latest": True,
                "name": "updated"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # old version of object should be _is_latest false

if __name__ == '__main__':
    unittest.main()
