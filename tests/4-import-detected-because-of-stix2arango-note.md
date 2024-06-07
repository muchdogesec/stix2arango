## TEST 4: Import same exactly the same bundle 3 times BUT with different stix2arango note to force update

This tests the logic of where an update to only the stix2arango_note changes, but the actual STIX objects remain the same

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle.json \
  --database s2a_tests \
  --collection test4 \
  --stix2arango_note test4A \
  --ignore_embedded_relationships false \
&& \
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle.json \
  --database s2a_tests \
  --collection test4 \
  --stix2arango_note test4B \
  --ignore_embedded_relationships false \
&& \
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle.json \
  --database s2a_tests \
  --collection test4 \
  --stix2arango_note test4C \
  --ignore_embedded_relationships false
```

```sql
RETURN LENGTH(
  FOR doc IN test4_vertex_collection
    FILTER doc._is_latest == true
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._stix2arango_note == "test4C"
      RETURN doc
)
```

Should return

```json
[
  3107
]
```

(number of objects in one bundle and b/c 4c considered latest)

```sql
RETURN LENGTH(
  FOR doc IN test4_vertex_collection
    FILTER doc._is_latest == false
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._stix2arango_note == "test4A"
    OR doc._stix2arango_note == "test4B"
      RETURN doc
)
```

Should return

```json
[
  6214
]
```

(3107 * 2 -- number of objects in two bundles and b/c 4a and 4b are considered older versions)


```sql
RETURN LENGTH(
  FOR doc IN test4_vertex_collection
    FILTER doc._is_latest == true
    AND doc._stix2arango_note == "automatically imported on collection creation"
      RETURN doc
)
```

Should return

```json
[
  12
]
```

(9 items from `templates/marking-definition.json`, `marking-definition/stix2arango.json`, `identity/stix2arango.json`, `identity/dogesec.json` = 12)

```sql
RETURN LENGTH(
  FOR doc IN test4_vertex_collection
    FILTER doc._is_latest == false
    AND doc._stix2arango_note == "automatically imported on collection creation"
      RETURN doc
)
```

Should return

```json
[
  0
]
```

(because only one version of auto imported objects should ever exist)

```sql
RETURN LENGTH(
  FOR doc IN test4_vertex_collection
    FILTER doc._stix2arango_note != "automatically imported on collection creation"
    AND doc.id == "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
      RETURN doc
)
```

Should return 

```json
[
  3
]
```

(b/c object is present in each update)

```sql
FOR doc IN test4_vertex_collection
    FILTER doc._stix2arango_note != "automatically imported on collection creation"
    AND doc.id == "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
    SORT doc._record_modified DESC
      RETURN {
        _stix2arango_note: doc._stix2arango_note,
        _is_latest: doc._is_latest,
        id: doc.id
      }
```

Should return

```json
[
  {
    "_stix2arango_note": "test4C",
    "_is_latest": true,
    "id": "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
  },
  {
    "_stix2arango_note": "test4B",
    "_is_latest": false,
    "id": "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
  },
  {
    "_stix2arango_note": "test4A",
    "_is_latest": false,
    "id": "indicator--d38c3e67-c14b-5d67-84c7-5400fb66d368"
  }
]
```

(the order of updates)

```sql
RETURN LENGTH(
  FOR doc IN test4_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == false
    AND doc._stix2arango_note == "test4C"
      RETURN doc
)
```

Should return:

```json
[
  914
]
```

(same number of relationships as in the bundle)

```sql
RETURN LENGTH(
  FOR doc IN test4_edge_collection
    FILTER doc._is_latest == false
    AND doc._is_ref == false
    AND doc._stix2arango_note == "test4A"
    OR doc._stix2arango_note == "test4B"
      RETURN doc
)
```

Should return:

```json
[
  1828
]
```

(old relationships x 2 = 914 x 2 = 1828)

```sql
RETURN LENGTH(
  FOR doc IN test4_edge_collection
      FILTER doc._is_ref == false
      AND doc.id == "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
        RETURN doc
)
```

Should return:

```json
[
  3
]
```

(As have been 3 updates)

```sql
FOR doc IN test4_edge_collection
  FILTER doc._is_ref == false
  AND doc.id == "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
  SORT doc._record_modified DESC
  RETURN {
    _stix2arango_note: doc._stix2arango_note,
    _is_latest: doc._is_latest,
    id: doc.id
  }
```

Should return 

```json
[
  {
    "_stix2arango_note": "test4C",
    "_is_latest": true,
    "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
  },
  {
    "_stix2arango_note": "test4B",
    "_is_latest": false,
    "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
  },
  {
    "_stix2arango_note": "test4A",
    "_is_latest": false,
    "id": "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
  }
]
```

(the order of updates)

```sql
RETURN LENGTH(
  FOR doc IN test4_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == true
    AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
    AND doc._stix2arango_note == "test4C"
      RETURN doc
)
```

Should return 

```json
[
  15032
]
```

(the number of embedded relationships in the bundle)

```sql
RETURN LENGTH(
  FOR doc IN test4_edge_collection
    FILTER doc._is_latest == false
    AND doc._is_ref == true
    AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
    AND doc._stix2arango_note == "test4A"
    OR doc._stix2arango_note == "test4B"
      RETURN doc
)
```

Should return

```json
[
  30064
]
```

(15302 x 2 for both old embedded relationships)

```sql
RETURN LENGTH(
  FOR doc IN test4_edge_collection
  FILTER doc._is_ref == true
  AND doc.id == "relationship--cffa89d7-4194-57b0-8ca2-0ff7473cd66a"
    RETURN doc
)
```

Should return 

```json
[
  3
]
```

(3 updates have happened)

```sql
FOR doc IN test4_edge_collection
  FILTER doc._is_ref == true
  AND doc.id == "relationship--cffa89d7-4194-57b0-8ca2-0ff7473cd66a"
  SORT doc._record_modified DESC
  RETURN {
    _stix2arango_note: doc._stix2arango_note,
    _is_latest: doc._is_latest,
    id: doc.id
  }
```

Should return

```json
[
  {
    "_stix2arango_note": "test4C",
    "_is_latest": true,
    "id": "relationship--cffa89d7-4194-57b0-8ca2-0ff7473cd66a"
  },
  {
    "_stix2arango_note": "test4B",
    "_is_latest": false,
    "id": "relationship--cffa89d7-4194-57b0-8ca2-0ff7473cd66a"
  },
  {
    "_stix2arango_note": "test4A",
    "_is_latest": false,
    "id": "relationship--cffa89d7-4194-57b0-8ca2-0ff7473cd66a"
  }
]
```