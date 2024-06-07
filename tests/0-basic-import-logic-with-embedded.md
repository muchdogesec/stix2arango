## TEST 0: New Import with embedded

A very basic test just to ensure basic import works.

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle.json \
  --database s2a_tests \
  --collection test0 \
  --stix2arango_note test0 \
  --ignore_embedded_relationships false
```

`sigma-rule-bundle.json` has

* grouping = 136 objects
* indicator = 2969 objects
* marking definition = 1 object
* identity = 1 object
3107 in vertex
* relationships = 914
914 in edge

```sql
RETURN LENGTH(
  FOR doc IN test0_vertex_collection
    FILTER doc._is_latest == true
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._stix2arango_note == "test0"
      RETURN doc
)
```

Should return

```json
[
  3107
]
```

(grouping 136 + indicator 2969 + marking definition 1 + identity 1 = 3,107)

```sql
RETURN LENGTH(
  FOR doc IN test0_vertex_collection
    FILTER doc._is_latest == false
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._stix2arango_note == "test0"
      RETURN doc
)
```

Should return

```json
[
  0
]
```

(as no updated versions imported yet)

```sql
RETURN LENGTH(
  FOR doc IN test0_vertex_collection
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
  FOR doc IN test0_vertex_collection
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
  FOR doc IN test0_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == false
    AND doc._stix2arango_note == "test0"
      RETURN doc
)
```

Should return:

```json
[
  914
]
```

(same number of relationships in the bundle)

```sql
RETURN LENGTH(
  FOR doc IN test0_edge_collection
    FILTER doc._is_latest == false
    AND doc._is_ref == false
    AND doc._stix2arango_note == "test0"
      RETURN doc
)
```

Should return:

```json
[
  0
]
```

(because no update have happened)

```sql
RETURN LENGTH(
  FOR doc IN test0_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == true
    AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
    AND doc._stix2arango_note == "test0"
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
  FOR doc IN test0_edge_collection
    FILTER doc._is_latest == false
    AND doc._is_ref == true
    AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
    AND doc._stix2arango_note == "test0"
      RETURN doc
)
```

Should return

```json
[
  0
]
```

(because no updates have happended yet)

```sql
RETURN LENGTH(
  FOR doc IN test0_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == true
    AND doc._stix2arango_note == "test0"
    AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
    AND doc.relationship_type == "target_ref"
    OR doc.relationship_type == "source_ref"
      RETURN doc
)
```

Should return

```json
[
  0
]
```

(because no embedded relationships should ever be generated from the `source_ref` and `target_ref` properties)

```sql
FOR doc IN test0_edge_collection
  FILTER doc._is_latest == true
  AND doc._is_ref == true
  AND doc._stix2arango_note == "test0"
  AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
    RETURN DISTINCT doc.relationship_type
```

Should return

```json
[
  "object_marking_refs",
  "created_by_ref",
  "object_refs"
]
```

(the unique embedded relationship keys that exist for this bundle)