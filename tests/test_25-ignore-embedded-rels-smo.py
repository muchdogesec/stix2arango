# python3 -m unittest tests/test_25-ignore-embedded-rels-smo.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test25"
        cls.STIX2ARANGO_NOTE_1 = "test25"
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "embedded-ref-sdo-sco-sro-smo.json"
        cls.TEST_FILE_2 = ""
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""
        cls.CUSTOM_FLAG_1 = "--ignore_embedded_relationships_smo true"
        cls.CUSTOM_FLAG_2 = ""
        cls.CUSTOM_FLAG_2 = ""

## SDO has 3 SCO has 2 SRO has 3 = 8

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test25_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [8]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the latest object has 3 refs

if __name__ == '__main__':
    unittest.main()
