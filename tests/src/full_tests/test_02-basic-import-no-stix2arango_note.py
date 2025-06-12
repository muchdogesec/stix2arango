# python3 -m unittest tests/test_02-basic-import-no-stix2arango_note.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test02"
        cls.FILES = [
            dict(file="sigma-rule-bundle.json", ignore_embedded_relationships=True)
        ]

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test02_vertex_collection
            FILTER doc._is_latest == true
            AND doc._stix2arango_note == ""
              RETURN doc
        )
        """
        expected_result = [3107]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # number of objects in bundle, and stix2arango_note was not entered via CLI

if __name__ == '__main__':
    unittest.main()
    