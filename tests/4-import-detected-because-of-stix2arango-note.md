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
  FOR doc IN test0_edge_collection
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