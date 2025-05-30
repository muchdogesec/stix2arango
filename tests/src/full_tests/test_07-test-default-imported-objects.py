# python3 -m unittest tests/test_07-test-default-imported-objects.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test07"
        cls.FILES = [
            dict(file="sigma-rule-bundle.json", ignore_embedded_relationships=False, stix2arango_note="test07"),
            dict(file="sigma-rule-bundle.json", ignore_embedded_relationships=False, stix2arango_note="test07"),
        ]



    def test_query_1(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test07_vertex_collection
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
            FOR doc IN test07_vertex_collection
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
    