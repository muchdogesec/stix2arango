# python3 -m unittest tests/test_01-basic-import-no-embedded.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test01"

        cls.FILES = [
            dict(file="sigma-rule-bundle.json", ignore_embedded_relationships=True, stix2arango_note="test01")
        ]

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test01_edge_collection
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
          FOR doc IN test01_edge_collection
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