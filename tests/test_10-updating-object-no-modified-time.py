# python3 -m unittest tests/test_10-updating-object-no-modified-time.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test10"
        cls.STIX2ARANGO_NOTE_1 = "test10"
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "sco-original.json"
        cls.TEST_FILE_2 = "sco-updated.json"
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test10_vertex_collection
                FILTER doc._is_latest == true
                AND doc._stix2arango_note != "automatically imported on collection creation"
                	RETURN doc
        )
        """
        expected_result = [2]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # b/c two objects in bundle

    def test_query_2(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test10_vertex_collection
                FILTER doc._is_latest == false
                AND doc._stix2arango_note != "automatically imported on collection creation"
                    RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # only 1 of the two objects is actually updated (only one object has properties changed between bundles)

    def test_query_3(self):
        query = """
        FOR doc IN test10_vertex_collection
            FILTER doc.id == "software--55388d12-8d7d-5ed1-b324-817a293a6854"
            SORT doc._is_latest DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
            }
        """
        expected_result = [
              {
                "id": "software--55388d12-8d7d-5ed1-b324-817a293a6854",
                "_is_latest": True
              },
              {
                "id": "software--55388d12-8d7d-5ed1-b324-817a293a6854",
                "_is_latest": False
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # this is the object that was updated

    def test_query_4(self):
        query = """
        FOR doc IN test10_vertex_collection
            FILTER doc.id == "software--6d38c3e0-ea8b-5b83-b370-5407523589a9"
            SORT doc._is_latest DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
            }
        """
        expected_result = [
              {
                "id": "software--6d38c3e0-ea8b-5b83-b370-5407523589a9",
                "_is_latest": False
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # this is the object that was updated

if __name__ == '__main__':
    unittest.main()
