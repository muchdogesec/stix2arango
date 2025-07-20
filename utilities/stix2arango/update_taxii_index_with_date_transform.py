import os
from dotenv import load_dotenv

import arango
import arango.exceptions
from arango.database import StandardDatabase
from arango import ArangoClient

from stix2arango.stix2arango.stix2arango import Stix2Arango

## run this like `ARANGODB_DATABASE=vulmatch_database python add_ref_types.py` if your database is created by any s2a version < 0.0.4

load_dotenv()

host_url = os.getenv('ARANGODB_HOST_URL')
client = ArangoClient(host_url, request_timeout=None)
PASSWORD = os.getenv('ARANGODB_PASSWORD')
db = client.db(username=os.getenv('ARANGODB_USERNAME'), password=PASSWORD, name=os.getenv('ARANGODB_DATABASE'))
collections = []
for collection in db.collections():
    collection_name: str = collection['name']
    if not (collection_name.endswith('_vertex_collection') or collection_name.endswith('_edge_collection')):
        continue
    c = db.collection(collection_name)
    indexes = {index['name']: index for index in c.indexes()}
    index = indexes.get('taxii_search')
    if index:
        c.delete_index('taxii_search')
    collections.append([c.count(), collection_name, c])

collections = dict(v[1:] for v in sorted(collections, key=lambda x: x[0]))

s2a = Stix2Arango(db.db_name, "", "", username=db.username, host_url=host_url, password=PASSWORD, create_collection=False, create_db=False)
s2a.arango.collections = collections
s2a.create_taxii_views()