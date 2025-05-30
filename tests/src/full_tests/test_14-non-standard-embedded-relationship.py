# python3 -m unittest tests/test_14-non-standard-embedded-relationship.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test14"
        cls.FILES = [
            dict(file="non-standard-embedded-relationship.json", ignore_embedded_relationships=False, stix2arango_note="test14"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test14_edge_collection
            FILTER doc._is_ref == true
              RETURN doc
        )
        """
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # number of _ref / _refs in bundle

    def test_query_2(self):
        query = """
        FOR doc IN test14_edge_collection
          FILTER doc._is_latest == true
          AND doc._is_ref == true
          AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
            SORT doc.relationship_type
            RETURN DISTINCT doc.relationship_type
        """
        expected_result = [
              "created-by",
              "non-standard"
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the type of _ref / _refs in bundle

if __name__ == '__main__':
    unittest.main()
      