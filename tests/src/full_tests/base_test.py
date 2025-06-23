import sys
import time
import unittest
from unittest.mock import patch
import requests
import base64
import json
import subprocess
import os
from dotenv import load_dotenv
from stix2arango.__main__ import main as run_s2a

# Load environment variables from .env file
load_dotenv()

ARANGODB_HOST = os.getenv("ARANGODB_HOST")
ARANGODB_PORT = os.getenv("ARANGODB_PORT")
ARANGODB_USERNAME = os.getenv("ARANGODB_USERNAME")
ARANGODB_PASSWORD = os.getenv("ARANGODB_PASSWORD")

class BaseTestArangoDBQueries(unittest.TestCase):

    script_run = False  # Class variable to ensure the script is run only once

    @classmethod
    def setUpClass(cls):
        cls.load_configuration()
        cls.clear_collections()
        if not cls.script_run:
            cls.run_script()
            cls.script_run = True
        cls.setup_headers_and_url()

    @classmethod
    def load_configuration(cls):
        cls.ARANGODB_DATABASE = os.getenv("ARANGODB_DATABASE")
        cls.ARANGODB_COLLECTION = os.getenv("ARANGODB_COLLECTION")
        cls.FILES: list[dict] = []


        cls.STIX2ARANGO_NOTE_1 = os.getenv("STIX2ARANGO_NOTE_1")
        cls.STIX2ARANGO_NOTE_2 = os.getenv("STIX2ARANGO_NOTE_2")
        cls.STIX2ARANGO_NOTE_3 = os.getenv("STIX2ARANGO_NOTE_3")
        cls.TEST_FILE_1 = os.getenv("TEST_FILE_1")
        cls.TEST_FILE_2 = os.getenv("TEST_FILE_2")
        cls.TEST_FILE_3 = os.getenv("TEST_FILE_3")
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_1 = os.getenv("IGNORE_EMBEDDED_RELATIONSHIPS_1")
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_2 = os.getenv("IGNORE_EMBEDDED_RELATIONSHIPS_2")
        cls.IGNORE_EMBEDDED_RELATIONSHIPS_3 = os.getenv("IGNORE_EMBEDDED_RELATIONSHIPS_3")
        cls.CUSTOM_FLAG_1 = os.getenv("CUSTOM_FLAG_1")
        cls.CUSTOM_FLAG_2 = os.getenv("CUSTOM_FLAG_2")
        cls.CUSTOM_FLAG_3 = os.getenv("CUSTOM_FLAG_3")

    @classmethod
    def clear_collections(cls):
        collections = [cls.ARANGODB_COLLECTION + '_vertex_collection', cls.ARANGODB_COLLECTION + '_edge_collection']
        for collection in collections:
            url = f'http://{ARANGODB_HOST}:{ARANGODB_PORT}/_db/{cls.ARANGODB_DATABASE}_database/_api/collection/{collection}/truncate'
            response = requests.put(url, headers={
                'Authorization': 'Basic ' + base64.b64encode(f'{ARANGODB_USERNAME}:{ARANGODB_PASSWORD}'.encode('utf-8')).decode('utf-8')
            })
            if response.status_code not in [200, 404]:
                raise Exception(f"Failed to clear collection {collection}: {response.text}")

    @classmethod
    def run_script(cls):
        for file in cls.FILES:
            args = ["stix2arango.py"]
            file.update(database=cls.ARANGODB_DATABASE, collection=cls.ARANGODB_COLLECTION, file=f"tests/files/stix2arango/{file['file']}")
            for k,v in file.items():
                args.append("--"+k)
                args.append(str(v))
            with patch.object(sys, 'argv', args):
                setup = run_s2a()
        return

    @classmethod
    def setup_headers_and_url(cls):
        cls.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode(f'{ARANGODB_USERNAME}:{ARANGODB_PASSWORD}'.encode('utf-8')).decode('utf-8')
        }
        cls.base_url = f'http://{ARANGODB_HOST}:{ARANGODB_PORT}/_db/{cls.ARANGODB_DATABASE}_database/_api/cursor'

    def query_arango(self, query):
        payload = json.dumps({'query': query})
        response = requests.post(self.base_url, headers=self.headers, data=payload)
        response.raise_for_status()
        return response.json()
