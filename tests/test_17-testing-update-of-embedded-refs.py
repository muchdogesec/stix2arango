# python3 -m unittest tests/test_17-testing-update-of-embedded-refs.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test17"
        cls.STIX2ARANGO_NOTE_1 = "test17"
        cls.STIX2ARANGO_NOTE_2 = "test17"
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "embedded-ref-object.json"
        cls.TEST_FILE_2 = "embedded-ref-object-updated.json"
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test17_edge_collection
            FILTER doc._is_ref == true
            AND doc._is_latest == true
              RETURN doc
        )
        """
        expected_result = [4]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # there are 4 embedded refs in the updated version of `indicator--49150a4c-d831-51fa-9f61-aede5570a969`

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test17_edge_collection
            FILTER doc._is_ref == true
            AND doc._is_latest == false
              RETURN doc
        )
        """
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # there are 3 embedded refs in the original version of `indicator--49150a4c-d831-51fa-9f61-aede5570a969`

    def test_query_3(self):
        query = """
        FOR doc IN test17_edge_collection
            FILTER doc._is_ref == true
            AND doc._is_latest == true
                RETURN DISTINCT doc.relationship_type
        """
        expected_result = [
              "created-by",
              "object-marking",
              "new"
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the distinct embedded ref objects in `indicator--49150a4c-d831-51fa-9f61-aede5570a969`

if __name__ == '__main__':
    unittest.main()
