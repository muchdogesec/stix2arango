# python3 -m unittest tests/test_22-embedded-sro-update-for-smo.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test22"
        cls.FILES = [
            dict(file="smo-embedded-ref-1.json", ignore_embedded_relationships=False, stix2arango_note="test22"),
            dict(file="smo-embedded-ref-2.json", ignore_embedded_relationships=False, stix2arango_note="test22"),
        ]


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
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # whilst the smo is updated with different md5 hash, the embedded sros created have exactly the same md5 hash, so it is not updated

    def test_query_3(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test22_edge_collection
            FILTER doc.id == "relationship--1cce4dca-d80c-5650-a9c2-858ad6707779"
            AND NOT HAS(doc, 'modified') AND HAS(doc, 'created') AND doc._is_latest
            RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # check created time exists

    def test_query_4(self):
        query = """
        FOR doc IN test22_edge_collection
            FILTER doc.id == "relationship--1cce4dca-d80c-5650-a9c2-858ad6707779" AND doc._is_latest
            RETURN {
                modified: doc.modified,
                created: doc.created
            }
        """
        expected_result = [
          {
            "modified": None,
            "created": "2016-08-01T00:00:00.000Z"
          }
        ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # follow up to test 3 checking that created property is as expected

if __name__ == '__main__':
    unittest.main()
