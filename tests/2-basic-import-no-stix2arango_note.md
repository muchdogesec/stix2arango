## TEST 2: Checking when no stix2arango_note added

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle.json \
  --database s2a_tests \
  --collection test2 \
  --ignore_embedded_relationships false
```

```sql
RETURN LENGTH(
  FOR doc IN test2_vertex_collection
    FILTER doc._is_latest == true
    AND doc._stix2arango_note == ""
      RETURN doc
)
```

Should return 

```json
[
  3107
]
```

(number of objects in bundle, and stix2arango_note was not entered via CLI)