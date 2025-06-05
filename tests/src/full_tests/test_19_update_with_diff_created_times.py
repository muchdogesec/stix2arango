# python3 -m unittest tests/test_19_update_with_diff_created_times.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test19"
        cls.FILES = [
            dict(file="update_with_diff_modified_times_1.json", ignore_embedded_relationships=False, stix2arango_note="test19"),
            dict(file="update_with_diff_modified_times_2.json", ignore_embedded_relationships=False, stix2arango_note="test19"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test19_vertex_collection
            FILTER doc._is_latest == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 1 object is latest

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test19_vertex_collection
            FILTER doc._is_latest == false
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [1]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # 1 object is old

if __name__ == '__main__':
    unittest.main()