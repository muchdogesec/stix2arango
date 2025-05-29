# python3 -m unittest tests/test_18-testing-nested-embedded-ref.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test18"
        cls.FILES = [
            dict(file="nested-embedded-ref.json", ignore_embedded_relationships=False, stix2arango_note="test18"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test18_edge_collection
            FILTER doc._is_ref == true
            AND doc._is_latest == true
              RETURN doc
        )
        """
        expected_result = [7]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # contains 4 address_ref and 3 object_marking refs

    def test_query_2(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test18_edge_collection
                FILTER doc._is_ref == true
                AND doc._is_latest == true
                AND doc.created != null
                AND doc.modified != null
                LET keys = ATTRIBUTES(doc)
                LET filteredKeys = keys[* FILTER !STARTS_WITH(CURRENT, "_")]
                RETURN KEEP(doc, filteredKeys)
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # this checks no created and modified times are generated in embedded SROS (because source transaction object does not have these times).

    def test_query_3(self):
        query = """
        FOR doc IN test18_edge_collection
            FILTER doc._is_ref == true
            AND doc._is_latest == true
            SORT doc.relationship_type
                RETURN DISTINCT doc.relationship_type
        """
        expected_result = [
              "object-marking",
              "output-address",
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the distinct embedded ref object relationship types for this search

    def test_query_4(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test18_edge_collection
                FILTER doc.id == "relationship--35f9c60e-5364-556e-a6f0-ccb0179eec02"
                COLLECT modified = doc.modified, created = doc.created
                RETURN { modified, created }
            )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # checks only one version with created and modified times exist, b/c no update yet

if __name__ == '__main__':
    unittest.main()
