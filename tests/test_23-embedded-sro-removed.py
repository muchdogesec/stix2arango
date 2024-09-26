# python3 -m unittest tests/test_23-embedded-sro-removed.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test23"
        cls.STIX2ARANGO_NOTE_1 = "test23"
        cls.STIX2ARANGO_NOTE_2 = "test23"
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "embedded-ref-object.json"
        cls.TEST_FILE_2 = "embedded-ref-object-removed.json"
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

# no embedded ref in the object now

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test23_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

# original bundle, the object had 3 objects

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test23_edge_collection
            FILTER doc._is_latest == false
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

if __name__ == '__main__':
    unittest.main()