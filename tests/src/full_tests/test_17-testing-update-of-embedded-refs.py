# python3 -m unittest tests/test_17-testing-update-of-embedded-refs.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test17"
        cls.FILES = [
            dict(file="embedded-ref-object.json", ignore_embedded_relationships=False, stix2arango_note="test17"),
            dict(file="embedded-ref-object-updated.json", ignore_embedded_relationships=False, stix2arango_note="test17"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test17_edge_collection
            FILTER doc._is_ref == true
            AND doc._is_latest == true
              RETURN doc
        )
        """
        expected_result = [4]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # there are 4 embedded refs in the updated version of `indicator--49150a4c-d831-51fa-9f61-aede5570a969`

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test17_edge_collection
            FILTER doc._is_ref == true
            AND doc._is_latest == false
              RETURN doc
        )
        """
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # there are 3 embedded refs in the original version of `indicator--49150a4c-d831-51fa-9f61-aede5570a969`

    def test_query_3(self):
        query = """
        FOR doc IN test17_edge_collection
            FILTER doc._is_ref == true
            AND doc._is_latest == true
            SORT doc.relationship_type
                RETURN DISTINCT doc.relationship_type
        """
        expected_result = [
              "created-by",
              "new",
              "object-marking",
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the distinct embedded ref objects in `indicator--49150a4c-d831-51fa-9f61-aede5570a969`

    def test_query_4(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test17_edge_collection
                FILTER doc._is_ref == true
                AND doc.id == "relationship--5b32a703-4317-5f58-b1ce-03735c756035"
                COLLECT modified = doc.modified, created = doc.created
                RETURN { modified, created }
            )
        """
        expected_result = [2]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # makes sure that the created and modified times are updated properly

if __name__ == '__main__':
    unittest.main()
