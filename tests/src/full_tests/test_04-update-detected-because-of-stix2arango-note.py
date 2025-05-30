# python3 -m unittest tests/test_04-update-detected-because-of-stix2arango-note.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test04"

        cls.FILES = [
            dict(file="sigma-rule-bundle.json", ignore_embedded_relationships=False, stix2arango_note="test04A"),
            dict(file="sigma-rule-bundle.json", ignore_embedded_relationships=False, stix2arango_note="test04B"),
            dict(file="sigma-rule-bundle.json", ignore_embedded_relationships=False, stix2arango_note="test04C"),
        ]

    def test_query_1(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_vertex_collection
                FILTER doc._is_latest == true
                AND doc._stix2arango_note != "automatically imported on collection creation"
                AND doc._stix2arango_note == "test04C"
                RETURN doc
        )
        """
        expected_result = [3107]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # number of objects in one bundle and b/c 4c considered latest

    def test_query_2(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_vertex_collection
                FILTER doc._is_latest == false
                AND doc._stix2arango_note != "automatically imported on collection creation"
                AND (doc._stix2arango_note == "test04A" OR doc._stix2arango_note == "test04B")
                RETURN doc
        )
        """
        expected_result = [6214]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 3107 * 2 -- number of objects in two bundles and
        # b/c 4a and 4b are considered older versions

    def test_query_3(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_vertex_collection
                FILTER doc._is_latest == true
                AND doc._stix2arango_note == "automatically imported on collection creation"
                RETURN doc
        )
        """
        expected_result = [12]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 9 items from `templates/marking-definition.json`, `marking-definition/stix2arango.json`,
        # `identity/stix2arango.json`, `identity/dogesec.json` = 12

    def test_query_4(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_vertex_collection
                FILTER doc._is_latest == false
                AND doc._stix2arango_note == "automatically imported on collection creation"
                RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because only one version of auto imported objects should ever exist

    def test_query_5(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_vertex_collection
                FILTER doc._stix2arango_note != "automatically imported on collection creation"
                AND doc.id == "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
                RETURN doc
        )
        """
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # b/c object is present in each update

    def test_query_6(self):
        query = """
        FOR doc IN test04_vertex_collection
            FILTER doc._stix2arango_note != "automatically imported on collection creation"
            AND doc.id == "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
            SORT doc._record_modified DESC
            RETURN {
                _stix2arango_note: doc._stix2arango_note,
                _is_latest: doc._is_latest,
                id: doc.id
            }
        """
        expected_result = [
            {
                "_stix2arango_note": "test04C",
                "_is_latest": True,
                "id": "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
            },
            {
                "_stix2arango_note": "test04B",
                "_is_latest": False,
                "id": "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
            },
            {
                "_stix2arango_note": "test04A",
                "_is_latest": False,
                "id": "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
            }
        ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the order of updates

    def test_query_7(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_edge_collection
                FILTER doc._is_latest == true
                AND doc._is_ref == false
                AND doc._stix2arango_note == "test04C"
                RETURN doc
        )
        """
        expected_result = [914]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # same number of relationships as in the bundle

    def test_query_8(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_edge_collection
                FILTER doc._is_latest == false
                AND doc._is_ref == false
                AND (doc._stix2arango_note == "test04A" OR doc._stix2arango_note == "test04B")
                RETURN doc
        )
        """
        expected_result = [1828]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # old relationships x 2 = 914 x 2 = 1828

    def test_query_9(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_edge_collection
                FILTER doc._is_ref == false
                AND doc.id == "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
                RETURN doc
        )
        """
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # As have been 3 updates

    def test_query_10(self):
        query = """
        FOR doc IN test04_edge_collection
            FILTER doc._is_ref == false
            AND doc.id == "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
            SORT doc._record_modified DESC
            RETURN {
                _stix2arango_note: doc._stix2arango_note,
                _is_latest: doc._is_latest,
                id: doc.id
            }
        """
        expected_result = [
            {
                "_stix2arango_note": "test04C",
                "_is_latest": True,
                "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
            },
            {
                "_stix2arango_note": "test04B",
                "_is_latest": False,
                "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
            },
            {
                "_stix2arango_note": "test04A",
                "_is_latest": False,
                "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
            }
        ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the order of updates

    def test_query_11(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_edge_collection
                FILTER doc._is_latest == true
                AND doc._is_ref == true
                AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
                AND doc._stix2arango_note == "test04C"
                RETURN doc
        )
        """
        expected_result = [15032]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the number of valid embedded relationships in the bundle

    def test_query_12(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_edge_collection
                FILTER doc._is_latest == false
                AND doc._is_ref == true
                AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
                AND (doc._stix2arango_note == "test04A" OR doc._stix2arango_note == "test04B")
                RETURN doc
        )
        """
        expected_result = [30064]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 15302 x 2 for both old embedded relationships

    def test_query_13(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_edge_collection
                FILTER doc._is_ref == true
                AND doc.id == "relationship--5b32a703-4317-5f58-b1ce-03735c756035"
                RETURN doc
        )
        """
        expected_result = [3]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 3 updates have happened

    def test_query_14(self):
        query = """
        RETURN LENGTH(
            FOR doc IN test04_edge_collection
                FILTER doc._is_ref == true
                AND doc._is_latest == true
                AND doc.id == "relationship--5b32a703-4317-5f58-b1ce-03735c756035"
                RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # but only one should be is latest

    def test_query_15(self):
        query = """
        FOR doc IN test04_edge_collection
            FILTER doc._is_ref == true
            AND doc.id == "relationship--5b32a703-4317-5f58-b1ce-03735c756035"
            SORT doc._record_modified DESC
            RETURN {
                _stix2arango_note: doc._stix2arango_note,
                _is_latest: doc._is_latest,
                id: doc.id
            }
        """
        expected_result = [
              {
                "_stix2arango_note": "test04C",
                "_is_latest": True,
                "id": "relationship--5b32a703-4317-5f58-b1ce-03735c756035"
              },
              {
                "_stix2arango_note": "test04B",
                "_is_latest": False,
                "id": "relationship--5b32a703-4317-5f58-b1ce-03735c756035"
              },
              {
                "_stix2arango_note": "test04A",
                "_is_latest": False,
                "id": "relationship--5b32a703-4317-5f58-b1ce-03735c756035"
              }
            ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the order of updates

if __name__ == '__main__':
    unittest.main()