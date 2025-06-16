import contextlib
from datetime import datetime
import logging
import os
from pathlib import Path
import sqlite3
import tempfile
import uuid
import ijson
import json
from collections import Counter

class BundleLoader:
    def __init__(self, file_path, chunk_size_min=20_000, db_path=""):
        self.file_path = Path(file_path)
        self.chunk_size_min = chunk_size_min
        self.groups = None
        self.bundle_id = "bundle--" + str(uuid.uuid4())

        self.db_path = db_path
        if not self.db_path:
            self.temp_path = tempfile.NamedTemporaryFile(prefix='s2a_bundle_loader--', suffix='.sqlite')
            self.db_path = self.temp_path.name
        self._init_db()

    def _init_db(self):
        """Initialize SQLite DB with objects table."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS objects (
                id TEXT PRIMARY KEY,
                type TEXT,
                raw TEXT
            )
        ''')
        self.conn.execute('PRAGMA synchronous = OFF;')
        self.conn.execute('PRAGMA journal_mode = MEMORY;')
        self.conn.execute('PRAGMA temp_store = MEMORY;')
        self.conn.commit()


    def save_to_sqlite(self, objects):
        """Save one STIX object to the SQLite database."""
        self.inserted = getattr(self, 'inserted', 0)

        try:
            self.conn.executemany(
                "INSERT OR REPLACE INTO objects (id, type, raw) VALUES (?, ?, ?)",
                [(obj['id'], obj['type'], json.dumps(obj)) for obj in objects]
            )
        except sqlite3.IntegrityError as e:
            print(f"Failed to insert len({objects}) objects: {e}")
        else:
            self.conn.commit()
        self.inserted += len(objects)
        # logging.info(f"inserted {self.inserted}")

    def build_groups(self):
        """
        Iterates the STIX bundle and uses union-find to group IDs such that for every
        relationship (object of type "relationship"), its own id and its source_ref
        and target_ref end up in the same group.
        """
        all_ids: dict[str, list[str]] = dict()  # All object IDs in the file
        logging.info(f"loading into {self.db_path}")
        
        with open(self.file_path, 'rb') as f:
            objects = ijson.items(f, 'objects.item', use_float=True)
            to_insert = []
            for obj in objects:
                obj_id = obj.get('id')
                to_insert.append(obj)
                all_ids.setdefault(obj_id, [])
                if obj['type'] == 'relationship' and all(x in obj for x in ['target_ref', 'source_ref']):
                    sr, tr = [obj['source_ref'], obj['target_ref']]
                    all_ids[obj_id].extend([sr, tr])
                    all_ids.setdefault(sr, []).extend([tr, obj_id])
                    all_ids.setdefault(tr, []).extend([sr, obj_id])
                if len(to_insert) >= self.chunk_size_min:
                    self.save_to_sqlite(to_insert)
                    to_insert.clear()
            if to_insert:
                self.save_to_sqlite(to_insert)
        
        logging.info(f"loaded {self.inserted} into {self.db_path}")
        handled = set()

        self.groups = []
        group = set()
        def from_ids(all_ids):
            for obj_id in all_ids:
                if obj_id in handled:
                    continue
                group_objs = {obj_id, *all_ids[obj_id]}
                handled.update(group_objs)
                new_group = group.union(group_objs)
                if len(new_group) >= self.chunk_size_min:
                    group.clear()
                    self.groups.append(tuple(new_group))
                else:
                    group.update(group_objs)

        from_ids(all_ids)
        if group:
            self.groups.append(tuple(group))
        return self.groups
    
    def load_objects_by_ids(self, ids):
        """Retrieve a list of STIX objects by their IDs from the SQLite database."""
        placeholders = ','.join(['?'] * len(ids))
        query = f"SELECT raw FROM objects WHERE id IN ({placeholders})"
        cursor = self.conn.execute(query, list(ids))
        return [json.loads(row[0]) for row in cursor.fetchall()]


    def get_objects(self, group):
        return list(self.load_objects_by_ids(group))
    
    @property
    def chunks(self):
        for group in self.groups or self.build_groups():
            yield self.get_objects(group)

    def __del__(self):
        with contextlib.suppress(Exception):
            os.remove(self.db_path)