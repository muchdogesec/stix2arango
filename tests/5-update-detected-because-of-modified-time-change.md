## TEST 5: Import a bundle 3 times BUT some objects have different `modified`. The modified times increase with each update

In this test 2 objects are updated each time (where modified time increases in order with each bundle)

* `relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35` 
  * modified time changes
* `indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd` 
  * modified time changes
  * name changes to: `Deny Service Access Using Security Descriptor Tampering Via Sc.EXE` -> `FIRST UPDATE` -> `SECOND UPDATE` 

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-original.json \
  --database s2a_tests \
  --collection test5 \
  --stix2arango_note test5 \
  --ignore_embedded_relationships false \
&& \
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-update-1.json \
  --database s2a_tests \
  --collection test5 \
  --stix2arango_note test5 \
  --ignore_embedded_relationships false \
&& \
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-update-2.json \
  --database s2a_tests \
  --collection test5 \
  --stix2arango_note test5 \
  --ignore_embedded_relationships false
```

`sigma-rule-bundle-condensed-original.json` (and updates) always have

* indicator = 2 objects
* identity = 1 object
* marking-definition = 1 object
* relationships = 1

```sql
RETURN LENGTH(
  FOR doc IN test5_vertex_collection
    FILTER doc._is_latest == true
    AND doc._stix2arango_note != "automatically imported on collection creation"
    RETURN doc
)
```

Should return

```json
[
  4
]
```

(4 non-relationship objects in bundle)

```sql
RETURN LENGTH(
  FOR doc IN test5_vertex_collection
    FILTER doc._is_latest == false
    AND doc._stix2arango_note != "automatically imported on collection creation"
    RETURN doc
)
```

Should return 

```json
[
  2
]
```

(one for each update of `indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd`)

```sql
FOR doc IN test5_vertex_collection
    FILTER doc._stix2arango_note != "automatically imported on collection creation"
    AND doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
    SORT doc._record_modified DESC
      RETURN {
        id: doc.id,
        _is_latest: doc._is_latest,
        name: doc.name,
        modified: doc.modified
      }
```

Should return:

```json
[
  {
    "id": "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd",
    "_is_latest": true,
    "name": "SECOND UPDATE",
    "modified": "2024-01-01T00:00:00.000Z"
  }
  {
    "id": "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd",
    "_is_latest": false,
    "name": "FIRST UPDATE",
    "modified": "2023-12-12T00:00:00.000Z"
  },
  {
    "id": "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd",
    "_is_latest": false,
    "name": "Deny Service Access Using Security Descriptor Tampering Via Sc.EXE",
    "modified": "2023-02-28T00:00:00.000Z"
  }
]
```

(the order of insert time with highest modified time as is latest = true)

```sql
RETURN LENGTH(
  FOR doc IN test5_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == false
      RETURN doc
)
```

Should return 

```json
[
  1
]
```

(only one relationship in bundle)

```sql
RETURN LENGTH(
  FOR doc IN test5_edge_collection
    FILTER doc._is_latest == false
    AND doc._is_ref == false
      RETURN doc
)
```

Should return 

```json
[
  2
]
```

(as 2 old versions of relationship object)

```sql
FOR doc IN test5_edge_collection
    FILTER doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_ref == false
    AND doc.id == "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
    SORT doc._record_modified DESC
      RETURN {
        id: doc.id,
        _is_latest: doc._is_latest,
        modified: doc.modified
      }
```

Should return:

```json
[
  {
    "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35",
    "_is_latest": true,
    "modified": "2024-01-01T00:00:00.000Z"
  },
  {
    "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35",
    "_is_latest": false,
    "modified": "2023-12-12T00:00:00.000Z"
  },
  {
    "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35",
    "_is_latest": false,
    "modified": "2023-02-28T00:00:00.000Z"
  }
]
```

```sql
RETURN LENGTH(
  FOR doc IN test5_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == true
      RETURN doc
)
```

Should return:

```json
[
  15
]
```

(there 15 valid `_ref` or `_refs` in final bundle)

```sql
RETURN LENGTH(
  FOR doc IN test5_edge_collection
    FILTER doc._is_latest == false
    AND doc._is_ref == true
      RETURN doc
)
```

Should return

```
[
  12
]
```

(only 1 indicator and 1 relationship are ever updated between updates, and between them they have 3 embedded relationships each (3x2)x2 = 12)

```sql
FOR doc IN test5_edge_collection
  FILTER doc._is_ref == true
  AND doc.id == "relationship--da230f89-3019-5016-8b40-695f343988ea"
  SORT doc._record_modified DESC
    RETURN {
      id: doc.id,
      _is_latest: doc._is_latest,
      modified: doc.modified
    }
```

Should return

```json
[
  {
    "id": "relationship--da230f89-3019-5016-8b40-695f343988ea",
    "_is_latest": true,
    "modified": "2024-01-01T00:00:00.000Z"
  },
  {
    "id": "relationship--da230f89-3019-5016-8b40-695f343988ea",
    "_is_latest": false,
    "modified": "2023-12-12T00:00:00.000Z"
  },
  {
    "id": "relationship--da230f89-3019-5016-8b40-695f343988ea",
    "_is_latest": false,
    "modified": "2023-02-28T00:00:00.000Z"
  }
]
```

(3 updates, highest modified time is always is latest)
