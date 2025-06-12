# python3 -m unittest tests/test_11-custom-sdos.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test11"
        cls.FILES = [
            dict(file="custom-sdo-original.json", ignore_embedded_relationships=False, stix2arango_note="test11"),
            dict(file="custom-sdo-updated.json", ignore_embedded_relationships=False, stix2arango_note="test11"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test11_vertex_collection
            FILTER doc._is_latest == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # number of objects in bundle

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test11_vertex_collection
            FILTER doc._is_latest == false
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # old version of object

    def test_query_3(self):
        query = """
        FOR doc IN test11_vertex_collection
            FILTER doc.id == "custom-sdo--cbc0b79a-ecbd-59f1-b45b-ea4730df1c2e"
            SORT doc.modified DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                modified: doc.modified
            }
        """
        expected_result = [
              {
                "id": "custom-sdo--cbc0b79a-ecbd-59f1-b45b-ea4730df1c2e",
                "_is_latest": True,
                "modified": "2024-01-01T00:00:00.000Z"
              },
              {
                "id": "custom-sdo--cbc0b79a-ecbd-59f1-b45b-ea4730df1c2e",
                "_is_latest": False,
                "modified": "2023-10-26T00:00:00.000Z"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # old version of object

if __name__ == '__main__':
    unittest.main()
