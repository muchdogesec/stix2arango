# python3 -m unittest tests/test_21-embedded-sro-update-for-sco.py

from full_tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test21"
        cls.FILES = [
            dict(file="nested-embedded-ref.json", ignore_embedded_relationships=False, stix2arango_note="test21"),
            dict(file="nested-embedded-ref.json", ignore_embedded_relationships=False, stix2arango_note="test21"),
        ]


    def test_query_1(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test21_edge_collection
            FILTER doc._is_latest == true
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [7]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the latest 4 address_ref and 3 object_marking refs latest version

    def test_query_2(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test21_edge_collection
            FILTER doc._is_latest == false
            AND doc._is_ref == true
            AND doc._stix2arango_note != "automatically imported on collection creation"
              RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # no update happens here because the updated SROs for embedded ref have identical properties

    def test_query_3(self):
        query = """
        RETURN LENGTH(
          FOR doc IN test21_edge_collection
            FILTER doc.id == "relationship--e33fa156-4d06-55e1-969e-97b25b68002d"
            AND HAS(doc, 'modified') OR HAS(doc, 'created')
            RETURN doc
        )
        """
        expected_result = [0]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # the embedded SRO should not have modified or created time because the source transaction object does not

    def test_query_4(self):
        query = """
        FOR doc IN test21_edge_collection
            FILTER doc.id == "relationship--e33fa156-4d06-55e1-969e-97b25b68002d"
            RETURN {
                modified: doc.modified,
                created: doc.created
            }
        """
        expected_result = [
          {
            "modified": None,
            "created": None
          }
        ]
        result = self.query_arango(query)
        self.assertEqual(result['result'], expected_result)

        # a follow up to test 3 to check these keys do not exist in object

if __name__ == '__main__':
    unittest.main()