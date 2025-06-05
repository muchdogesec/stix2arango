# python3 -m unittest tests/test_12-custom-scos.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test12"
        cls.FILES = [
            dict(file="custom-sco-original.json", ignore_embedded_relationships=False, stix2arango_note="test12"),
            dict(file="custom-sco-updated.json", ignore_embedded_relationships=False, stix2arango_note="test12"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test12_vertex_collection
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
          FOR doc IN test12_vertex_collection
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
        FOR doc IN test12_vertex_collection
            FILTER doc.id == "custom-sco--0306ac42-a167-4eb6-a67a-969c255a85ae"
            SORT doc._is_latest DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                name: doc.title
            }
        """
        expected_result = [
              {
                "id": "custom-sco--0306ac42-a167-4eb6-a67a-969c255a85ae",
                "_is_latest": True,
                "name": "new"
              },
              {
                "id": "custom-sco--0306ac42-a167-4eb6-a67a-969c255a85ae",
                "_is_latest": False,
                "name": "old"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # old version of object should be _is_latest false

if __name__ == '__main__':
    unittest.main()
