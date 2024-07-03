# python3 -m unittest tests/test_07-test-default-imported-objects.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test7"
        cls.STIX2ARANGO_NOTE_1 = "test7"
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "sigma-rule-bundle.json"
        cls.TEST_FILE_2 = "sigma-rule-bundle.json"
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = "false"


    def test_query_1(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test3_vertex_collection
                FILTER doc._is_latest == true
                AND doc._stix2arango_note == "automatically imported on collection creation"
                RETURN doc
        )
        """
        expected_result = [12]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 9 items from `templates/marking-definition.json`, `marking-definition/stix2arango.json`,
        # `identity/stix2arango.json`, `identity/dogesec.json` = 12

    def test_query_2(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test3_vertex_collection
                FILTER doc._is_latest == false
                AND doc._stix2arango_note == "automatically imported on collection creation"
                RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because these objects should never be updated

if __name__ == '__main__':
    unittest.main()
    