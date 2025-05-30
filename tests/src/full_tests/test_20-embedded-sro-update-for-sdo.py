# python3 -m unittest tests/test_20-embedded-sro-update-for-sdo.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test20"
        cls.FILES = [
            dict(file="embedded-ref-object.json", ignore_embedded_relationships=False, stix2arango_note="test20"),
            dict(file="embedded-ref-object-updated.json", ignore_embedded_relationships=False, stix2arango_note="test20"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test20_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [4]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the latest object has ref properties

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test20_edge_collection
            FILTER doc._is_latest == false
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the old object had 3 ref properties

    def test_query_3(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test20_edge_collection
            FILTER doc.id == "relationship--5b32a703-4317-5f58-b1ce-03735c756035"
            AND HAS(doc, 'modified') AND HAS(doc, 'created')
            RETURN doc
        )
        """
        expected_result = [2]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the embedded SRO should have modified and created time because the source indicator object does

    def test_query_4(self):
        query = """
        FOR doc IN test20_edge_collection
            FILTER doc.id == "relationship--5b32a703-4317-5f58-b1ce-03735c756035"
            SORT doc.modified
            RETURN {
                modified: doc.modified,
                created: doc.created
            }
        """
        expected_result = [
          {
            "modified": "2023-02-14T00:00:00.000Z",
            "created": "2021-12-07T00:00:00.000Z"
          },
          {
            "modified": "2024-02-14T00:00:00.000Z",
            "created": "2021-12-07T00:00:00.000Z"
          }
        ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # check modified times are correct

if __name__ == '__main__':
    unittest.main()