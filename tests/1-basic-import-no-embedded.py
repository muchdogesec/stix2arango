# python3 -m unittest tests/1-basic-import-no-embedded.py

from .base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test1"
        cls.STIX2ARANGO_NOTE_1 = "test1"
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "sigma-rule-bundle.json"
        cls.TEST_FILE_2 = ""
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "true"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test1_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == true
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because embedded relationships are set to false

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test1_edge_collection
            FILTER doc._is_latest == false
            AND doc._is_ref == true
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because embedded relationships are set to false

if __name__ == '__main__':
    unittest.main()