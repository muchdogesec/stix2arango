# python3 -m unittest tests/test_13-updating-smos.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test13"
        cls.FILES = [
            dict(file="smo-original.json", ignore_embedded_relationships=False, stix2arango_note="test13"),
            dict(file="smo-updated.json", ignore_embedded_relationships=False, stix2arango_note="test13"),
            dict(file="smo-updated-2.json", ignore_embedded_relationships=False, stix2arango_note="test13"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test13_vertex_collection
            FILTER doc._is_latest == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # only one latest version

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test13_vertex_collection
            FILTER doc._is_latest == false
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [2]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 2 old versions should exist

    def test_query_3(self):
        query = """
        FOR doc IN test13_vertex_collection
            FILTER doc.id == "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41aa"
            SORT doc.name ASC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                name: doc.name,
                created: doc.created
            }
        """
        expected_result = [
              {
                "id": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41aa",
                "_is_latest": False,
                "name": "original",
                "created": "2016-08-01T00:00:00.000Z"
              },
              {
                "id": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41aa",
                "_is_latest": False,
                "name": "updated",
                "created": "2016-08-01T00:00:00.000Z"
              },
              {
                "id": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41aa",
                "_is_latest": True,
                "name": "UPDATED 2",
                "created": "2023-08-01T00:00:00.000Z"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # old version of object should be _is_latest false

if __name__ == '__main__':
    unittest.main()
