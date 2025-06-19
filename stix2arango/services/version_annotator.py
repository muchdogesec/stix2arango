from collections import defaultdict
import os
import time
from typing import List, Dict
import copy

from datetime import datetime
import os
import typing
from arango.client import ArangoClient
from arango.database import StandardDatabase


def annotate_versions(objects: List[Dict]):
    grouped = defaultdict(list)

    # Group by 'id'
    for obj in objects:
        grouped[obj['id']].append(obj)

    result: list[dict] = []
    deprecated = []

    for obj_id, items in grouped.items():
        # items = [copy.deepcopy(item) for item in items]

        # Separate items with non-None modified
        valid_modified = [item for item in items if item.get('modified') is not None]

        # _is_latest: max(modified) -> max(_record_modified)
        if valid_modified:
            max_modified = max(item.get('modified') for item in valid_modified)
            latest_candidates = [item for item in valid_modified if item.get('modified') == max_modified]
            max_record_modified_latest = max(item['_record_modified'] for item in latest_candidates)
        else:
            max_modified = None
            max_record_modified_latest = max(item['_record_modified'] for item in items)
        # _is_earliest: min(modified) -> max(_record_modified)
        if valid_modified:
            min_modified = min(item.get('modified') for item in valid_modified)
            earliest_candidates = [item for item in valid_modified if item.get('modified') == min_modified]
            max_record_modified_earliest = max(item['_record_modified'] for item in earliest_candidates)
        else:
            min_modified = None
            max_record_modified_earliest = min(item['_record_modified'] for item in items)

        # _taxii_visible: for each modified (including None), select highest _record_modified
        taxii_visible_keys = set()
        modified_groups = defaultdict(list)
        for item in items:
            modified_groups[item.get('modified')].append(item)

        for mod_val, group in modified_groups.items():
            max_rec_mod = max(i['_record_modified'] for i in group)
            for item in group:
                if item['_record_modified'] == max_rec_mod:
                    taxii_visible_keys.add(item['_key'])

        for item in items:
            is_latest = (
                item.get('modified') == max_modified
                and item['_record_modified'] == max_record_modified_latest
            )

            is_earliest = (
                item.get('modified') == min_modified
                and item['_record_modified'] == max_record_modified_earliest
            )

            if item.get('_is_latest') and not is_latest:
                deprecated.append(item['_id'])
            item['_is_latest'] = is_latest
            item['_taxii'] = dict(visible=item['_key'] in taxii_visible_keys, first=is_earliest, last=is_latest)
            result.append(item)

    return result, deprecated
