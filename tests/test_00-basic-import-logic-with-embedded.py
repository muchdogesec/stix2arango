# python3 -m unittest tests/test_00-basic-import-logic-with-embedded.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test0"
        cls.STIX2ARANGO_NOTE_1 = "test0"
        cls.STIX2ARANGO_NOTE_2 = ""
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "sigma-rule-bundle.json"
        cls.TEST_FILE_2 = ""
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_vertex_collection
            FILTER doc._is_latest == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
            AND doc._stix2arango_note == "test0"
              RETURN doc
        )
        """
        expected_result = [3107]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # grouping 136 + indicator 2969 + marking definition 1 + identity 1 = 3,107

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_vertex_collection
            FILTER doc._is_latest == false
            AND doc._stix2arango_note != "automatically imported on collection creation"
            AND doc._stix2arango_note == "test0"
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # as no updated versions imported yet

    def test_query_3(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_vertex_collection
            FILTER doc._is_latest == false
            AND doc._stix2arango_note == "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because only one version of auto imported objects should ever exist

    def test_query_4(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == false
            AND doc._stix2arango_note == "test0"
              RETURN doc
        )
        """
        expected_result = [914]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # same number of relationships in the bundle

    def test_query_5(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_edge_collection
            FILTER doc._is_latest == false
            AND doc._is_ref == false
            AND doc._stix2arango_note == "test0"
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because no update have happened

    def test_query_6(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == true
            AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
            AND doc._stix2arango_note == "test0"
              RETURN doc
        )
        """
        expected_result = [15032]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the number of embedded relationships in the bundle

    def test_query_7(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_edge_collection
            FILTER doc._is_latest == false
            AND doc._is_ref == true
            AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
            AND doc._stix2arango_note == "test0"
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because no updates have happended yet

    def test_query_8(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == true
            AND doc._stix2arango_note == "test0"
            AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
            AND doc.relationship_type == "target_ref"
            OR doc.relationship_type == "source_ref"
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # because no embedded relationships should ever be generated from the `source_ref` and `target_ref` properties

    def test_query_9(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_edge_collection
            FILTER doc._stix2arango_ref_err == true
              RETURN {
                stix2arango_ref_err: doc._stix2arango_ref_err,
                id: doc.id
              }
            )
        """
        expected_result = [167]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # note all relationships in bundle and all embedded ref ids exist in bundle.
        # this query will show you those erronous objects
        #
        #LET vertex_ids = (
        #  FOR v IN test0_vertex_collection
        #  RETURN v.id
        #)
        #
        #FOR doc IN test0_edge_collection
        #    FILTER doc._stix2arango_ref_err == true
        #    LET source_missing = POSITION(vertex_ids, doc.source_ref) == false
        #    LET target_missing = POSITION(vertex_ids, doc.target_ref) == false
        #    RETURN {
        #        stix2arango_ref_err: doc._stix2arango_ref_err,
        #        id: doc.id,
        #        source_ref: doc.source_ref,
        #        target_ref: doc.target_ref,
        #        missing_object_ids: APPEND(
        #            source_missing ? [doc.source_ref] : [],
        #            target_missing ? [doc.target_ref] : []
        #       )
        #    }

    def test_query_10(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test0_edge_collection
            FILTER doc._stix2arango_ref_err == false
              RETURN {
                stix2arango_ref_err: doc._stix2arango_ref_err,
                id: doc.id
              }
            )
        """
        expected_result = [15779]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

    def test_query_11(self):
        query = """
        FOR doc IN test0_edge_collection
          FILTER doc._is_latest == true
          AND doc._is_ref == true
          AND doc._stix2arango_note == "test0"
          AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
            RETURN DISTINCT doc.relationship_type
        """
        expected_result = {
            "object-marking",
            "created-by",
            "object"
        }
        result = self.query_arango(query)
        self.assertEqual(set(result['result']), expected_result)

        # the unique embedded relationship keys that exist for this bundle

if __name__ == '__main__':
    unittest.main()
