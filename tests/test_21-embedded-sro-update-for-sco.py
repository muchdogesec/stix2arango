# python3 -m unittest tests/test_21-embedded-sro-update-for-sco.py

from tests.base_test import BaseTestArangoDBQueries

class TestArangoDBQueries(BaseTestArangoDBQueries):

    @classmethod
    def load_configuration(cls):
        super().load_configuration()
        cls.ARANGODB_DATABASE = "s2a_tests"
        cls.ARANGODB_COLLECTION = "test21"
        cls.STIX2ARANGO_NOTE_1 = "test21"
        cls.STIX2ARANGO_NOTE_2 = "test21"
        cls.STIX2ARANGO_NOTE_3 = ""
        cls.TEST_FILE_1 = "nested-embedded-ref.json"
        cls.TEST_FILE_2 = "nested-embedded-ref.json"
        cls.TEST_FILE_3 = ""
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = "false"
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = ""