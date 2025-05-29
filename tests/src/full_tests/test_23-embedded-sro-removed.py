# python3 -m unittest tests/test_23-embedded-sro-removed.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test23"
        cls.FILES = [
            dict(file="embedded-ref-object.json", ignore_embedded_relationships=False, stix2arango_note="test23"),
            dict(file="embedded-ref-object-removed.json", ignore_embedded_relationships=False, stix2arango_note="test23"),
        ]


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