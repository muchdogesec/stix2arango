# python3 -m unittest tests/test_22-embedded-sro-update-for-smo.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test22"
        cls.STIX2ARANGO_NOTE_1 = "test22"
        cls.STIX2ARANGO_NOTE_2 = "test22"
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "smo-embedded-ref-1.json"
        cls.TEST_FILE_2 = "smo-embedded-ref-2.json"
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test22_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the latest object has 3 refs

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test22_edge_collection
            FILTER doc._is_latest == false
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 

    def test_query_3(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test22_edge_collection
            FILTER doc.id == "relationship--1cce4dca-d80c-5650-a9c2-858ad6707779"
            AND NOT HAS(doc, 'modified') AND HAS(doc, 'created')
            RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 

    def test_query_4(self):
        query = """
        FOR doc IN test22_edge_collection
            FILTER doc.id == "relationship--1cce4dca-d80c-5650-a9c2-858ad6707779"
            RETURN {
                modified: doc.modified,
                created: doc.created
            }
        """
        expected_result = [
          {
            "modified": null,
            "created": "2016-08-01T00:00:00.000Z"
          }
        ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 

if __name__ == '__main__':
    unittest.main()