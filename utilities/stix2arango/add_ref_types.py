import os
from dotenv import load_dotenv

import arango
import arango.exceptions
from arango.database import StandardDatabase
from arango import ArangoClient

## run this like `ARANGODB_DATABASE=vulmatch_database python add_ref_types.py` if your database is created by any s2a version < 0.0.4

load_dotenv()

client = ArangoClient(os.getenv('ARANGODB_HOST_URL'), request_timeout=None)
db = client.db(username=os.getenv('ARANGODB_USERNAME'), password=os.getenv('ARANGODB_PASSWORD'), name=os.getenv('ARANGODB_DATABASE'))
for c in db.collections():
    collection_name = c['name']
    if not collection_name.endswith('_edge_collection'):
        continue
    collection = db.collection(collection_name)
    print('updating collection objects with _target_type and _source_type where missing')
    print('this may take a while, depending on collection size')
    print('collection:', collection_name, 'in db:', db.name)
    db.aql.execute("""
        FOR doc IN @@collection
        FILTER doc.type == 'relationship'
        UPDATE {_key: doc._key} WITH {_source_type: FIRST(SPLIT(doc.source_ref, "--")), _target_type: FIRST(SPLIT(doc.target_ref, "--"))} IN @@collection
        """, bind_vars={'@collection': collection_name})
    