## Existing tests

* test 0: single import to test that when embedded relationship setting is set to true, they are created
* test 1: single import to test that when embedded relationship setting is set to ignore, that no embedded relationships are actually generated
* test 2: single import to check `_stix2arango_note` property can be left blank, but still appears in created records (as empty)
* test 3: This tests the logic of where an update to an object represents no change at all
* test 4: This tests the logic of where an update to only the `_stix2arango_note` property changes
* test 5: This tests the logic of where an update to only the `modified` property changes. The bundles are imported with the lowest `modifed` time first and highest `modified` time last (in time order)
* test 6: almost identical to 5, however, the bundles are imported in reverse order with the highest `modifed` time first and lowest `modified` time last (in reverse time order)
* test 7: makes sure default imported objects are imported correctly, and that they are not updated between updates
* test 8: contains a bundle with 2 sets of duplicate objects (both exact copies)
* test 9: similar to test 8, but now one of the duplicate object has a `modified` time change
* test 10: testing updates of SCOs (where no `modified` property exists)
* test 11: testing custom SDOs (where `modified` time exists)
* test 12: testing custom SCOs (where no `modified` property exists)
* test 13: testing updates of SMOs (where only `created` time exists)
* test 14: tesing the generation of emedded relationships that are non-standard (in STIX spec)

## Running tests

Run 

```shell
pytest
```

from the root directory of this code.

## Description of test files

### `sigma-rule-bundle-condensed-*`

* sigma-rule-bundle-condensed-original.json
* sigma-rule-bundle-condensed-update-1.json
* sigma-rule-bundle-condensed-update-2.json

In these files 2 objects are modified each time.

The `modified` times for the objects increases in order with each bundle (e.g original has lowest time, -2 has highest time)

Objects modified are

* `relationship--3089bdec-3d25-5d1b-a6ac-9d152ab14e35` 
  * modified time changes
* `indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd` 
  * modified time changes
  * name changes to: `Deny Service Access Using Security Descriptor Tampering Via Sc.EXE` -> `FIRST UPDATE` -> `SECOND UPDATE` 

### `duplicate-objects-all-properties-same.json`

Has 2 objects:

* `indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd`
* `software--50fa0834-9c63-5b0f-bf0e-dce02183253a`

Printed in the bundle twice

### `duplicate-objects-properties-different.json`

Has 3 objects:

* `relationship--00038d0e-7fc7-41c3-9055-edb4d87ea912`
  * has 2 `modified` times
* `indicator--7a5dedb9-30f9-51c0-a49d-91aeda1fd7fd`
  * has 2 `modified` times
* `software--50fa0834-9c63-5b0f-bf0e-dce02183253a`
  * 2 duplicate versions

### `sco-original.json`, `sco-updated.json`

* `software--55388d12-8d7d-5ed1-b324-817a293a6854`
  * `name` property is update between bundles
* `software--6d38c3e0-ea8b-5b83-b370-5407523589a9`
  * object is identical in each bundle

### `custom-sdo-original.json`, `custom-sdo-updated.json`

* `custom-sdo--cbc0b79a-ecbd-59f1-b45b-ea4730df1c2e`
  * `modified` and `name` values changed between updates

### `custom-sco-original.json`, `custom-sco-updated.json`

* `custom-sco--0306ac42-a167-4eb6-a67a-969c255a85ae`
  * `title` changes between updates







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