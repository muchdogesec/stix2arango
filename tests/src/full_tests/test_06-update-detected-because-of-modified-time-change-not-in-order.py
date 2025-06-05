# python3 -m unittest tests/test_06-update-detected-because-of-modified-time-change-not-in-order.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test06"
        cls.FILES = [
            dict(file="sigma-rule-bundle-condensed-update-2.json", ignore_embedded_relationships=False, stix2arango_note="test06"),
            dict(file="sigma-rule-bundle-condensed-update-1.json", ignore_embedded_relationships=False, stix2arango_note="test06"),
            dict(file="sigma-rule-bundle-condensed-original.json", ignore_embedded_relationships=False, stix2arango_note="test06"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test06_vertex_collection
                FILTER doc._is_latest == true
                AND doc._stix2arango_note != "automatically imported on collection creation"
                RETURN doc
        )
        """
        expected_result = [4]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 4 non-relationship objects in bundle

    def test_query_2(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test06_vertex_collection
                FILTER doc._is_latest == false
                AND doc._stix2arango_note != "automatically imported on collection creation"
                RETURN doc
        )
        """
        expected_result = [2]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # one for each update of `indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd`

    def test_query_3(self):
        query = """
        FOR doc IN test06_vertex_collection
            FILTER doc._stix2arango_note != "automatically imported on collection creation"
            AND doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
            SORT doc.modified DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                name: doc.name,
                modified: doc.modified
            }
        """
        expected_result = [
            {
                "id": "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd",
                "_is_latest": True,
                "name": "SECOND UPDATE",
                "modified": "2024-01-01T00:00:00.000Z"
            },
            {
                "id": "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd",
                "_is_latest": False,
                "name": "FIRST UPDATE",
                "modified": "2023-12-12T00:00:00.000Z"
            },
            {
                "id": "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd",
                "_is_latest": False,
                "name": "Deny Service Access Using Security Descriptor Tampering Via Sc.EXE",
                "modified": "2023-02-28T00:00:00.000Z"
            }
        ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the order of insert time with highest modified time as is latest = true

    def test_query_4(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test06_edge_collection
                FILTER doc._is_latest == true
                AND doc._is_ref == false
                RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # only one relationship in bundle

    def test_query_5(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test06_edge_collection
                FILTER doc._is_latest == false
                AND doc._is_ref == false
                RETURN doc
        )
        """
        expected_result = [2]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # as 2 old versions of relationship object

    def test_query_6(self):
        query = """
        FOR doc IN test06_edge_collection
            FILTER doc._stix2arango_note != "automatically imported on collection creation"
            AND doc._is_ref == false
            AND doc.id == "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
            SORT doc.modified DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                modified: doc.modified
            }
        """
        expected_result = [
            {
                "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35",
                "_is_latest": True,
                "modified": "2024-01-01T00:00:00.000Z"
            },
            {
                "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35",
                "_is_latest": False,
                "modified": "2023-12-12T00:00:00.000Z"
            },
            {
                "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35",
                "_is_latest": False,
                "modified": "2023-02-28T00:00:00.000Z"
            }
        ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the order of insert time with highest modified time as is latest = true

    def test_query_7(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test06_edge_collection
                FILTER doc._is_latest == true
                AND doc._is_ref == true
                RETURN doc
        )
        """
        expected_result = [15]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # there 15 valid `_ref` or `_refs` in final bundle

    def test_query_8(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test06_edge_collection
                FILTER doc._is_latest == false
                AND doc._is_ref == true
                RETURN doc
        )
        """
        expected_result = [12]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # only 1 indicator and 1 relationship are ever updated between updates
        # and between them they have 3 embedded relationships each (3x2)x2 = 12

    def test_query_9(self):
        query = """
        FOR doc IN test06_edge_collection
            FILTER doc._is_ref == true
            AND doc.id == "relationship--6b91fcdc-997d-5317-ae08-c001fb6d6d08"
            SORT doc.modified DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                modified: doc.modified
            }
        """
        expected_result = [
              {
                "id": "relationship--6b91fcdc-997d-5317-ae08-c001fb6d6d08",
                "_is_latest": True,
                "modified": "2023-02-28T00:00:00.000Z"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # this object is not updated so only one is_ref object ever created

    def test_query_10(self):
        query = """
        FOR doc IN test06_edge_collection
            FILTER doc._is_ref == true
            AND doc.id == "relationship--5f8d9c38-5c00-53e2-b520-01694d0f8085"
            SORT doc.modified DESC
            RETURN {
                id: doc.id,
                _is_latest: doc._is_latest,
                modified: doc.modified
            }
        """
        expected_result = [
              {
                "id": "relationship--5f8d9c38-5c00-53e2-b520-01694d0f8085",
                "_is_latest": True,
                "modified": "2024-01-01T00:00:00.000Z"
              },
              {
                "id": "relationship--5f8d9c38-5c00-53e2-b520-01694d0f8085",
                "_is_latest": False,
                "modified": "2023-12-12T00:00:00.000Z"
              },
              {
                "id": "relationship--5f8d9c38-5c00-53e2-b520-01694d0f8085",
                "_is_latest": False,
                "modified": "2023-02-28T00:00:00.000Z"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 3 updates, highest modified time is always is latest

if __name__ == '__main__':
    unittest.main()
