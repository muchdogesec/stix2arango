## TEST 1: New Import withOUT embedded

A very basic test just to ensure basic import works.

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle.json \
  --database s2a_tests \
  --collection test1 \
  --stix2arango_note test1 \
  --ignore_embedded_relationships true
```

```sql
RETURN LENGTH(
  FOR doc IN test1_edge_collection
    FILTER doc._is_latest == true
    AND doc._is_ref == true
    AND doc._stix2arango_note == "test1"
    AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
      RETURN doc
)
```

Should return 

```json
[
  0
]
```

(because embedded relationships are set to false)

```sql
RETURN LENGTH(
  FOR doc IN test1_edge_collection
    FILTER doc._is_latest == false
    AND doc._is_ref == true
    AND doc._stix2arango_note == "test1"
    AND doc.created_by_ref == "identity--72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4"
      RETURN doc
)
```

Should return

```json
[
  0
]
```

(because embedded relationships are set to false)
