# python3 -m unittest tests/test_18-testing-nested-embedded-ref.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test18"
        cls.STIX2ARANGO_NOTE_1 = ""
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "nested-embedded-ref.json"
        cls.TEST_FILE_2 = ""
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test18_edge_collection
            FILTER doc._is_ref == true
            AND doc._is_latest == true
              RETURN doc
        )
        """
        expected_result = [7]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # contains 4 address_ref and 3 object_marking refs


if __name__ == '__main__':
    unittest.main()