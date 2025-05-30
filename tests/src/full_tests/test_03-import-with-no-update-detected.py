# python3 -m unittest tests/test_03-import-with-no-update-detected.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test03"

        cls.FILES = [
            dict(file="sigma-rule-bundle.json", ignore_embedded_relationships=False, stix2arango_note="test03"),
            dict(file="sigma-rule-bundle-another.json", ignore_embedded_relationships=False, stix2arango_note="test03"),
            dict(file="sigma-rule-bundle-yet-another.json", ignore_embedded_relationships=False, stix2arango_note="test03"),
        ]

    def test_query_1(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test03_vertex_collection
                FILTER doc._is_latest == true
                AND doc._stix2arango_note != "automatically imported on collection creation"
                AND doc._stix2arango_note == "test03"
                RETURN doc
        )
        """
        expected_result = [3107]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # grouping 136 + indicator 2969 + marking definition 1 + identity 1 = 3,107

    def test_query_2(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test03_vertex_collection
                FILTER doc._is_latest == false
                AND doc._stix2arango_note != "automatically imported on collection creation"
                AND doc._stix2arango_note == "test03"
                RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # as no updates ever happen between versions

    def test_query_3(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test03_edge_collection
                FILTER doc._is_latest == true
                AND doc._is_ref == false
                AND doc._stix2arango_note == "test03"
                RETURN doc
        )
        """
        expected_result = [914]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # same number of relationships in the bundle

    def test_query_4(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test03_edge_collection
                FILTER doc._is_latest == false
                AND doc._is_ref == false
                AND doc._stix2arango_note == "test03"
                RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because no update should have happened

    def test_query_5(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test03_edge_collection
                FILTER doc._is_latest == true
                AND doc._is_ref == true
                AND doc._stix2arango_note == "test03"
                RETURN doc
        )
        """
        expected_result = [15032]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the number of embedded relationships in the bundle

    def test_query_6(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test03_edge_collection
                FILTER doc._is_latest == false
                AND doc._is_ref == true
                AND doc._stix2arango_note == "test03"
                RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because no update should have happened

if __name__ == '__main__':
    unittest.main()
