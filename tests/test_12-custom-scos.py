# python3 -m unittest tests/test_12-custom-scos.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test12"
        cls.STIX2ARANGO_NOTE_1 = "test12"
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "custom-sco-original.json"
        cls.TEST_FILE_2 = "custom-sco-updated.json"
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test12_vertex_collection
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
          FOR doc IN test12_vertex_collection
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
        FOR doc IN test12_vertex_collection
            FILTER doc.id == "custom-sco--0306ac42-a167-4eb6-a67a-969c255a85ae"
            SORT doc._is_latest DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                name: doc.title
            }
        """
        expected_result = [
              {
                "id": "custom-sco--0306ac42-a167-4eb6-a67a-969c255a85ae",
                "_is_latest": True,
                "name": "new"
              },
              {
                "id": "custom-sco--0306ac42-a167-4eb6-a67a-969c255a85ae",
                "_is_latest": False,
                "name": "old"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # old version of object should be _is_latest false

if __name__ == '__main__':
    unittest.main()
