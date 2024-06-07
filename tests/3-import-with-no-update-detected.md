## TEST 2: Import same exactly the same bundle 3 times, to check update behaviour

This tests the logic of where an update to an object represents no change at all.

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle.json \
  --database s2a_tests \
  --collection test3 \
  --stix2arango_note test3 \
  --ignore_embedded_relationships false \
&& \
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle.json \
  --database s2a_tests \
  --collection test3 \
  --stix2arango_note test3 \
  --ignore_embedded_relationships false \
&& \
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle.json \
  --database s2a_tests \
  --collection test3 \
  --stix2arango_note test3 \
  --ignore_embedded_relationships false
```

```sql
RETURN LENGTH(
  FOR doc IN test3_vertex_collection
    FILTER doc._is_latest == true
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._stix2arango_note == "test3"
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
  FOR doc IN test3_vertex_collection
    FILTER doc._is_latest == false
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._stix2arango_note == "test3"
      RETURN doc
)
```

Should return

```json
[
  0
]
```

(as no updates ever happen between versions)

```sql
RETURN LENGTH(
  FOR doc IN test3_vertex_collection
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
  FOR doc IN test3_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == false
    AND doc._stix2arango_note == "test3"
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
  FOR doc IN test3_edge_collection
    FILTER doc._is_latest == false
    AND doc._is_ref == false
    AND doc._stix2arango_note == "test3"
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
  FOR doc IN test3_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == true
    AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
    AND doc._stix2arango_note == "test3"
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
  FOR doc IN test3_edge_collection
    FILTER doc._is_latest == false
    AND doc._is_ref == true
    AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
    AND doc._stix2arango_note == "test3"
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