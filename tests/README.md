## Existing tests

* test 0: single import to test that when embedded relationship setting is set to true, they are created
* test 1: single import to test that when embedded relationship setting is set to ignore, that no embedded relationships are actually generated
* test 2: single import to check `_stix2arango_note` property can be left blank, but still appears in created records (as empty)
* test 3: This tests the logic of where an update to an object represents no change at all
* test 4: This tests the logic of where an update to only the `_stix2arango_note` property changes
* test 5: This tests the logic of where an update to only the `modified` property changes. The bundles are imported with the lowest `modifed` time first and highest `modified` time last (in time order)
* test 6: almost identical to 5, however, the bundles are imported in reverse order with the highest `modifed` time first and lowest `modified` time last (in reverse time order)
* test 7: makes sure default imported objects are imported correctly, and that they are not updated between updates




## Running tests

Run 

```shell
pytest
```

from the root directory of this code.

e.g. running all tests:

```shell
python3 -m unittest tests/0-basic-import-logic-with-embedded.py && \
python3 -m unittest tests/1-basic-import-no-embedded.py && \
python3 -m unittest tests/ && \
python3 -m unittest tests/ && \
python3 -m unittest tests/ && \
python3 -m unittest tests/ && \
python3 -m unittest tests/ && \
python3 -m unittest tests/ && \
python3 -m unittest tests/ && \
python3 -m unittest tests/ && \

```

## TEST 3: Testing SDO update of all objects using `stix2arango_note`

This time were testing changes where the STIX objects in the bundle remain the same with each update, but the `_stix2arango_note` value is changed. This should update ALL objects, as this property is considered in the hash of the file.

As times are identical between objects, the latest import should be treated as the most recent.

```shell
python3 stix2arango.py \
	--file tests/files/sigma-rule-bundle-condensed-original.json \
	--database s2a_tests \
	--collection test3 \
	--stix2arango_note v1.0 && \
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-original.json \
  --database s2a_tests \
  --collection test3 \
  --stix2arango_note v2.0
```

```sql
RETURN LENGTH(
  FOR doc IN test3_vertex_collection
    FILTER doc._stix2arango_note == "v1.0"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == true
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Search should return 0 results, because these are old objects

```sql
RETURN LENGTH(
  FOR doc IN test3_vertex_collection
    FILTER doc._stix2arango_note == "v1.0"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == false
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Should return 4 results, the old versions.

```sql
RETURN LENGTH(
  FOR doc IN test3_vertex_collection
    FILTER doc._stix2arango_note == "v2.0"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == true
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Should return 4 results as these are the new objects.

```sql
RETURN LENGTH(
  FOR doc IN test3_vertex_collection
    FILTER doc._stix2arango_note == "v2.0"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == false
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Should return 0 results.

```sql
RETURN LENGTH(
  FOR doc IN test3_edge_collection
    FILTER doc._stix2arango_note == "v1.0"
    AND doc._is_latest == true
    AND doc._is_ref == false
    RETURN doc
)
```

Should return 0 results as this is the old SRO.

```sql
RETURN LENGTH(
  FOR doc IN test3_edge_collection
    FILTER doc._stix2arango_note == "v2.0"
    AND doc._is_latest == true
    AND doc._is_ref == false
    RETURN doc
)
```

Should return 1 result, the updated SRO.

```sql
RETURN LENGTH(
  FOR doc IN test3_edge_collection
    FILTER doc._stix2arango_note == "v1.0"
    AND doc._is_latest == true
    AND doc._is_ref == true
    RETURN doc
)
```

Should return 0 result, as these are old objects

```sql
RETURN LENGTH(
  FOR doc IN test3_edge_collection
    FILTER doc._stix2arango_note == "v1.0"
    AND doc._is_latest == false
    AND doc._is_ref == true
    RETURN doc
)
```

Should return 15 results, the old embedded relationships objects

```sql
RETURN LENGTH(
  FOR doc IN test3_edge_collection
    FILTER doc._stix2arango_note == "v2.0"
    AND doc._is_latest == true
    AND doc._is_ref == true
    RETURN doc
)
```

Should return 15 results, the new embedded relationships objects

```sql
RETURN LENGTH(
  FOR doc IN test3_edge_collection
    FILTER doc._stix2arango_note == "v2.0"
    AND doc._is_latest == false
    AND doc._is_ref == true
    RETURN doc
)
```

Should return 0 result, as these are new objects

## TEST 3.5: Same as 3 but with random values

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-original.json \
  --database s2a_tests \
  --collection test3_5 \
  --stix2arango_note foo && \
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-original.json \
  --database s2a_tests \
  --collection test3_5 \
  --stix2arango_note bar
```

```sql
RETURN LENGTH(
  FOR doc IN test3_5_vertex_collection
    FILTER doc._stix2arango_note == "foo"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == true
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Search should return 0 results, because these are old objects

```sql
RETURN LENGTH(
  FOR doc IN test3_5_vertex_collection
    FILTER doc._stix2arango_note == "foo"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == false
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Should return 4 results, the old versions.

```sql
RETURN LENGTH(
  FOR doc IN test3_5_vertex_collection
    FILTER doc._stix2arango_note == "bar"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == true
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Should return 4 results as these are the new objects.

```sql
RETURN LENGTH(
  FOR doc IN test3_5_vertex_collection
    FILTER doc._stix2arango_note == "bar"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == false
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Should return 0 results, because these are old objects.

## TEST 4: Testing SDO update of all objects using `stix2arango_note`, however, this time the one object has a created and modified time that are different, so times should take precedence

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-update-2.json \
  --database s2a_tests \
  --collection test4 \
  --stix2arango_note foo && \
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-original.json \
  --database s2a_tests \
  --collection test4 \
  --stix2arango_note v1.0
```

```sql
RETURN LENGTH(
  FOR doc IN test4_vertex_collection
    FILTER doc._stix2arango_note == "foo"
    AND doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == true
    AND doc._file_name == "sigma-rule-bundle-condensed-update-2.json"
    RETURN doc
)
```

Search should return 1 result, as this foo version has the highest modified time

```sql
RETURN LENGTH(
  FOR doc IN test4_vertex_collection
    FILTER doc._stix2arango_note == "v1.0"
    AND doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == true
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Should return 0 results, as this is the latest version.

```sql
RETURN LENGTH(
  FOR doc IN test4_vertex_collection
    FILTER doc._stix2arango_note == "v1.0"
    AND doc.id != "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == true
    AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
    RETURN doc
)
```

Should return 3 results, as in this case v1.0 is the latest for all other objects in the bundle.

```sql
RETURN LENGTH(
  FOR doc IN test4_vertex_collection
    FILTER doc._stix2arango_note == "foo"
    AND doc.id != "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
    AND doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == false
    AND doc._file_name == "sigma-rule-bundle-condensed-update-2.json"
    RETURN doc
)
```

Should return 3 results, as in this case foo is the old version for all other objects in the bundle.

## TEST 5: Testing no embedded relationships

```shell
python3 stix2arango.py \
	--file tests/files/sigma-rule-bundle-condensed-original.json \
	--database s2a_tests \
	--collection test5 \
	--ignore_embedded_relationships true
```

```sql
RETURN LENGTH(
  FOR doc IN test5_edge_collection
    FILTER doc._is_ref == true
    AND doc._is_latest == true
    RETURN doc
)
```

Should return 0 results, because embedded relationships have been ignored.

```sql
RETURN LENGTH(
  FOR doc IN test5_edge_collection
    FILTER doc._is_ref == false
    AND doc._is_latest == true
    RETURN doc
)
```

Should return 1 result for the SROs in bundle.

```sql
RETURN LENGTH(
  FOR doc IN test5_edge_collection
    FILTER doc._is_ref == false
    AND doc._is_latest == false
    RETURN doc
)
```

Should return 0 results, as no updates been made.

## TEST 6: Testing SCO updates

In this bundle, 1 SCO is updated. In this test, we're testing how SCOs with no time values are updated. It's expected that the last imported objects become the latest, when a change to md5 hash is observed.

```shell
python3 stix2arango.py \
	--file tests/files/sco-original.json \
	--database s2a_tests \
	--collection test6 && \
python3 stix2arango.py \
  --file tests/files/sco-updated.json \
  --database s2a_tests \
  --collection test6
```

```sql
RETURN LENGTH(
  FOR doc IN test6_vertex_collection
    FILTER doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == true
    RETURN doc
)
```

Should return 2 results

```sql
RETURN LENGTH(
  FOR doc IN test6_vertex_collection
    FILTER doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == false
    RETURN doc
)
```

Should return 1 result, the updated SCO.

```sql
FOR doc IN test6_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "software--55388d12-8d7d-5ed1-b324-817a293a6854"
  AND doc._is_latest == true
  AND NOT CONTAINS(doc._key, "+")
  AND ["marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9", "marking-definition--de23ef3b-83bf-56a9-95c3-46bc1703966c"] ALL IN doc.object_marking_refs
  AND doc.name == "New name"
  AND doc._file_name == "sco-updated.json"
  RETURN doc
```

Should return the new object.

```sql
FOR doc IN test6_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "software--55388d12-8d7d-5ed1-b324-817a293a6854"
  AND doc._is_latest == false
  AND CONTAINS(doc._key, "+")
  AND ["marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9", "marking-definition--de23ef3b-83bf-56a9-95c3-46bc1703966c"] ALL IN doc.object_marking_refs
  AND doc.name == "sha2 Project sha2 0.4.1 for Rust"
  AND doc._file_name == "sco-original.json"
  RETURN doc
```

Should return the old object.

## TEST 7: Testing SCO updates (other way around)

Simply reverse the order of the last test, importing the objects the other way around which will change which object is considered the latest.

```shell
python3 stix2arango.py \
	--file tests/files/sco-updated.json \
	--database s2a_tests \
	--collection test7 && \
python3 stix2arango.py \
	--file tests/files/sco-original.json \
	--database s2a_tests \
	--collection test7
```

```sql
FOR doc IN test7_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "software--55388d12-8d7d-5ed1-b324-817a293a6854"
  AND doc._is_latest == true
  AND NOT CONTAINS(doc._key, "+")
  AND doc._file_name == "sco-original.json"
  AND ["marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9", "marking-definition--de23ef3b-83bf-56a9-95c3-46bc1703966c"] ALL IN doc.object_marking_refs
  AND doc.name == "sha2 Project sha2 0.4.1 for Rust"
  RETURN doc
```

Should return 1 result, the new object.

```sql
FOR doc IN test7_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "software--55388d12-8d7d-5ed1-b324-817a293a6854"
  AND doc._is_latest == false
  AND CONTAINS(doc._key, "+")
  AND doc._file_name == "sco-updated.json"
  AND ["marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9", "marking-definition--de23ef3b-83bf-56a9-95c3-46bc1703966c"] ALL IN doc.object_marking_refs
  AND doc.name == "New name"
  RETURN doc
```

Should return 1 result, the old object.

## TEST 8: Testing SRO updates

Here we're testing SRO updates. In short these should behave the same as SDOs.

In this bundle one SRO is updated.

```shell
python3 stix2arango.py \
	--file tests/files/sro-original.json \
	--database s2a_tests \
	--collection test8 && \
python3 stix2arango.py \
	--file tests/files/sro-updated.json \
	--database s2a_tests \
	--collection test8
```

```sql
FOR doc IN test8_edge_collection
  FILTER doc._is_ref == false
  AND doc._is_latest == true
  AND NOT CONTAINS(doc._key, "+")
  AND doc.id == "relationship--00038d0e-7fc7-41c3-9055-edb4d87ea912"
  AND doc.x_mitre_version == "2.0"
  AND doc.description == " updated"
  AND doc.relationship_type == "updated"
  AND doc._file_name == "sro-updated.json"
  RETURN doc
```

Should return 1 results, the new object.

```sql
FOR doc IN test8_edge_collection
  FILTER doc._is_ref == false
  AND doc._is_latest == false
  AND CONTAINS(doc._key, "+")
  AND doc.id == "relationship--00038d0e-7fc7-41c3-9055-edb4d87ea912"
  AND doc.x_mitre_version == "1.0"
  AND doc.description == "[Explosive](https://attack.mitre.org/software/S0569) has collected the MAC address from the victim's machine.(Citation: CheckPoint Volatile Cedar March 2015)"
  AND doc.relationship_type == "uses"
  AND doc._file_name == "sro-original.json"
  RETURN doc
```

Should return 1 results, the old object.

```sql
RETURN LENGTH(
	FOR doc IN test8_vertex_collection
	  FILTER doc._stix2arango_note != "automatically imported on collection creation"
	  AND doc._is_latest == false
	  RETURN doc
)
```

Should return 0 results as no vertex objects are updated between bundles.

## TEST 9: Testing SRO updates (newest object added first)

Same as 8, but the other way around. As modified time present, expect the same output as 8.

```shell
python3 stix2arango.py \
	--file tests/files/sro-updated.json \
	--database s2a_tests \
	--collection test9 && \
python3 stix2arango.py \
	--file tests/files/sro-original.json \
	--database s2a_tests \
	--collection test9
```

```sql
FOR doc IN test9_edge_collection
  FILTER doc._is_ref == false
  AND doc._is_latest == true
  AND NOT CONTAINS(doc._key, "+")
  AND doc.id == "relationship--00038d0e-7fc7-41c3-9055-edb4d87ea912"
  AND doc.x_mitre_version == "2.0"
  AND doc.description == " updated"
  AND doc.relationship_type == "updated"
  AND doc._file_name == "sro-updated.json"
  RETURN doc
```

Should return 1 results, the new object.

```sql
FOR doc IN test9_edge_collection
  FILTER doc._is_ref == false
  AND doc._is_latest == false
  AND CONTAINS(doc._key, "+")
  AND doc.id == "relationship--00038d0e-7fc7-41c3-9055-edb4d87ea912"
  AND doc.x_mitre_version == "1.0"
  AND doc.description == "[Explosive](https://attack.mitre.org/software/S0569) has collected the MAC address from the victim's machine.(Citation: CheckPoint Volatile Cedar March 2015)"
  AND doc.relationship_type == "uses"
  AND doc._file_name == "sro-original.json"
  RETURN doc
```

Should return 1 results, the old object.

```sql
RETURN LENGTH(
  FOR doc IN test9_vertex_collection
    FILTER doc._stix2arango_note != "automatically imported on collection creation"
    AND doc._is_latest == false
    RETURN doc
)
```

Should return 0 results as no vertex objects are updated between bundles.

## TEST 10: Testing custom objects with date fields (aka SDO, SRO, or language content SMO)

```shell
python3 stix2arango.py \
  --file tests/files/custom-sdo-original.json \
  --database s2a_tests \
  --collection test10 && \
python3 stix2arango.py \
  --file tests/files/custom-sdo-updated.json \
  --database s2a_tests \
  --collection test10
```

```sql
FOR doc IN test10_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "custom-sdo--cbc0b79a-ecbd-59f1-b45b-ea4730df1c2e"
  AND doc._is_latest == false
  AND CONTAINS(doc._key, "+")
  AND doc._file_name == "custom-sdo-original.json"
  AND doc.name == "Sensitive Cookie Without 'HttpOnly' Flag"
  RETURN doc
```

Should return 1 result, the old object.

```sql
FOR doc IN test10_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "custom-sdo--cbc0b79a-ecbd-59f1-b45b-ea4730df1c2e"
  AND doc._is_latest == true
  AND NOT CONTAINS(doc._key, "+")
  AND doc._file_name == "custom-sdo-updated.json"
  AND doc.name == "UPDATED"
  RETURN doc
```

## TEST 11: Testing custom objects with NO date fields (aka SCO)

```shell
python3 stix2arango.py \
  --file tests/files/custom-sco-original.json \
  --database s2a_tests \
  --collection test11 && \
python3 stix2arango.py \
  --file tests/files/custom-sco-updated.json \
  --database s2a_tests \
  --collection test11
```

```sql
FOR doc IN test11_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "custom-sco--0306ac42-a167-4eb6-a67a-969c255a85ae"
  AND doc._is_latest == false
  AND CONTAINS(doc._key, "+")
  AND doc._file_name == "custom-sco-original.json"
  AND doc.title == "old"
  RETURN doc
```

Should return 1 result, the old object.

```sql
FOR doc IN test11_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "custom-sco--0306ac42-a167-4eb6-a67a-969c255a85ae"
  AND doc._is_latest == true
  AND NOT CONTAINS(doc._key, "+")
  AND doc._file_name == "custom-sco-updated.json"
  AND doc.title == "new"
  RETURN doc
```

Should return 1 result, the new object.

## TEST 12: Testing custom objects with only created fields (aka marking definitions SMO)

Here, we expect the object to be treated like an SCO, so the latest version should be the last imported object.

```shell
python3 stix2arango.py \
  --file tests/files/smo-original.json \
  --database s2a_tests \
  --collection test12 && \
python3 stix2arango.py \
  --file tests/files/smo-updated.json \
  --database s2a_tests \
  --collection test12
```

```sql
FOR doc IN test12_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da"
  AND doc._is_latest == false
  AND CONTAINS(doc._key, "+")
  AND doc._file_name == "smo-original.json"
  AND doc.definition.statement == "Copyright 2019, Example Corp"
  RETURN doc
```

Should return 1 object, the old one.

```sql
FOR doc IN test12_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da"
  AND doc._is_latest == true
  AND NOT CONTAINS(doc._key, "+")
  AND doc._file_name == "smo-updated.json"
  AND doc.definition.statement == "UPDATED"
  RETURN doc
```

## TEST 13: Testing custom objects SMO other way around

Same as 12, but other way around. Expecting opposite results.

```shell
python3 stix2arango.py \
  --file tests/files/smo-updated.json \
  --database s2a_tests \
  --collection test13 && \
python3 stix2arango.py \
  --file tests/files/smo-original.json \
  --database s2a_tests \
  --collection test13
```

```sql
FOR doc IN test13_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da"
  AND doc._is_latest == true
  AND NOT CONTAINS(doc._key, "+")
  AND doc._file_name == "smo-original.json"
  AND doc.definition.statement == "Copyright 2019, Example Corp"
  RETURN doc
```

Should return 1 result, the new object

```sql
FOR doc IN test13_vertex_collection
  FILTER doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.id == "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da"
  AND doc._is_latest == false
  AND CONTAINS(doc._key, "+")
  AND doc._file_name == "smo-updated.json"
  AND doc.definition.statement == "UPDATED"
  RETURN doc
```

Should return 1 result, the old object

## TEST 14: Testing `_record_modified` / `_record_created` are generated correctly

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-original.json \
  --database s2a_tests \
  --collection test14
```

WAIT ROUGHLY 20 SECONDS (just a period of time that can be used to easily test timings)

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-update-2.json \
  --database s2a_tests \
  --collection test14
```

```sql
FOR doc IN test14_vertex_collection
  FILTER doc._is_latest == false
  AND doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.name == "Deny Service Access Using Security Descriptor Tampering Via Sc.EXE"
  AND doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
  AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
  AND CONTAINS(doc._key, "+")
  RETURN doc
```

The oldest (1 result). Check `_record_modified` / `_record_created` are equal.

```sql
FOR doc IN test14_vertex_collection
  FILTER doc._is_latest == true
  AND doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.name == "SECOND UPDATE"
  AND doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
  AND doc._file_name == "sigma-rule-bundle-condensed-update-2.json"
  AND NOT CONTAINS(doc._key, "+")
  RETURN doc
```

The latest (1 result). Check `_record_created` is equal to old object. Check `_record_modified` is 20 seconds (or however long you waited) after old object.

```sql
FOR doc IN test14_edge_collection
  FILTER doc._is_latest == false
  AND doc._is_ref == false
  AND doc.id == "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
  AND doc.modified == "2023-02-28T00:00:00.000Z"
  AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
  AND CONTAINS(doc._key, "+")
  RETURN doc
```

The oldest (1 result). Check `_record_modified` / `_record_created` are equal.

```sql
FOR doc IN test14_edge_collection
  FILTER doc._is_latest == true
  AND doc._is_ref == false
  AND doc.id == "relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35"
  AND doc.modified == "2024-01-01T00:00:00.000Z"
  AND doc._file_name == "sigma-rule-bundle-condensed-update-2.json"
  AND NOT CONTAINS(doc._key, "+")
  RETURN doc
```

The latest (1 result). Check `_record_created` is equal to old object. Check `_record_modified` is 20 seconds (or however long you waited) after old object.

```sql
FOR doc IN test14_edge_collection
  FILTER doc._is_latest == false
  AND doc._is_ref == true
  AND doc.source_ref == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
  AND CONTAINS(doc._key, "+")
  AND ["marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9", "marking-definition--efccc0ba-d237-5c9a-ad41-4f8bb6791be4"] ALL IN doc.object_marking_refs
  AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
  AND doc.id == "relationship--ffa82506-ad5f-52e9-a0e1-a8a01c013077"
  AND doc.created_by_ref == "identity--c54d8eea-d241-5a83-8bf1-619f215ce10b"
  RETURN doc
```

The oldest embedded SRO (1 result). Check `_record_modified` / `_record_created` are equal.

```sql
FOR doc IN test14_edge_collection
  FILTER doc._is_latest == true
  AND doc._is_ref == true
  AND doc.source_ref == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
  AND NOT CONTAINS(doc._key, "+")
  AND ["marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9", "marking-definition--efccc0ba-d237-5c9a-ad41-4f8bb6791be4"] ALL IN doc.object_marking_refs
  AND doc._file_name == "sigma-rule-bundle-condensed-update-2.json"
  AND doc.id == "relationship--ffa82506-ad5f-52e9-a0e1-a8a01c013077"
  AND doc.created_by_ref == "identity--c54d8eea-d241-5a83-8bf1-619f215ce10b"
  RETURN doc
```

Here are the embedded new objects from the embedded. Check `_record_created` is equal to old object. Check `_record_modified` is 20 seconds (or however long you waited) after old object.

Now add middle object to check update times (the object generated here should be is latest = false);

```shell
python3 stix2arango.py \
  --file tests/files/sigma-rule-bundle-condensed-update-1.json \
  --database s2a_tests \
  --collection test14
```

```sql
FOR doc IN test14_vertex_collection
  FILTER doc._is_latest == false
  AND doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.name == "Deny Service Access Using Security Descriptor Tampering Via Sc.EXE"
  AND doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
  AND doc._file_name == "sigma-rule-bundle-condensed-original.json"
  AND CONTAINS(doc._key, "+")
  RETURN doc
```

The oldest (1 result). Check `_record_modified` / `_record_created` are equal.

```sql
FOR doc IN test14_vertex_collection
  FILTER doc._is_latest == true
  AND doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.name == "SECOND UPDATE"
  AND doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
  AND doc._file_name == "sigma-rule-bundle-condensed-update-2.json"
  AND NOT CONTAINS(doc._key, "+")
  RETURN doc
```

The newest object. Check `_record_created` is equal to old object. Check `_record_modified` is 20 seconds (or however long you waited) after old object.

```sql
FOR doc IN test14_vertex_collection
  FILTER doc._is_latest == false
  AND doc._stix2arango_note != "automatically imported on collection creation"
  AND doc.name == "FIRST UPDATE"
  AND doc.id == "indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd"
  AND doc._file_name == "sigma-rule-bundle-condensed-update-1.json"
  AND CONTAINS(doc._key, "+")
  RETURN doc
```

The middle result, but `_record_modified` should be same as latest result.

## TEST 15: Test custom embedded relationships

```shell
python3 stix2arango.py \
  --file tests/files/arango-cti-capec-update.json \
  --database s2a_tests \
  --collection test15
```

```sql
FOR doc IN test15_edge_collection
  FILTER doc._is_latest == true
  AND doc._is_ref == true
  AND doc.created_by_ref == "identity--c54d8eea-d241-5a83-8bf1-619f215ce10b"
  COLLECT relationshipType = doc.relationship_type
  RETURN relationshipType
```

Will show all embedded relationship types, which should be...

```json
[
  "created_by_ref",
  "object_marking_refs",
  "x_capec_can_precede_refs",
  "x_capec_child_of_refs",
  "x_capec_parent_of_refs"
]
```