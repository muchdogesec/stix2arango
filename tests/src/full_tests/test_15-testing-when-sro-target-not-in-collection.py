# python3 -m unittest tests/test_15-testing-when-sro-target-not-in-collection.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test15"
        cls.FILES = [
            dict(file="target-object-does-not-exist.json", ignore_embedded_relationships=True, stix2arango_note="test15"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test15_edge_collection
              RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the one relationship should exist

    def test_query_2(self):
        query = """
        FOR doc IN test15_edge_collection
            FILTER doc.id == "relationship--00038d0e-7fc7-41c3-9055-edb4d87ea912"
                AND doc._stix2arango_ref_err == true
                RETURN {
                _stix2arango_ref_err: doc._stix2arango_ref_err,
                id: doc.id
            }
        """
        expected_result = [
              {
                "_stix2arango_ref_err": True,
                "id": "relationship--00038d0e-7fc7-41c3-9055-edb4d87ea912"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because the target does not exist, the relationship should show a _stix2arango_ref_err property
                  