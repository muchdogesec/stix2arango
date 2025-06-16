# python3 -m unittest tests/test_26-ignore-embedded-rels-sro.py

import unittest
from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test26"


        cls.FILES = [
            dict(file="embedded-ref-sdo-sco-sro-smo.json", ignore_embedded_relationships=False, stix2arango_note="test26", ignore_embedded_relationships_smo=True),
        ]


## SDO has 3 SCO has 2 SMO has 3 = 8

    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test26_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [8]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the latest object has 3 refs

if __name__ == '__main__':
    unittest.main()
