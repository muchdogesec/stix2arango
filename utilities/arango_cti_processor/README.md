## arango_cti_processor

Downloads and imports files to ArangoDB used as the base data for arango_cti_processor.

To run these scripts, from the root of stix2arango;

```shell
python3 utilities/arango_cti_processor/SCRIPT
```

Where:

* `SCRIPT` (required): is either
	* `insert_archive_attack_enterprise.py`
	* `insert_archive_attack_ics.py`
	* `insert_archive_attack_mobile.py`
	* `insert_archive_capec.py`
	* `insert_archive_cwe.py`
	* `insert_archive_disarm.py`
	* `insert_archive_location.py`
	* `insert_archive_sigma_rules.py`
	* `insert_archive_yara_rules.py`
	* `insert_archive_tlp.py`
	* `insert_archive_atlas.py`
	
* `--database` (required): is the name of the Arango database the objects should be stored in. If database does not exist, stix2arango will create it
* `--ignore_embedded_relationships` (optional): if flag passed this will stop any embedded relationships from being generated.
* `--versions` (optional): are one or more of the versions listed in each script. e.g. for `insert_archive_disarm.py` are currently `1_2`, `1_3`, `1_4`. If no `version` flag is passed, all listed versions will be downloaded. IMPORTANT: flag does not work with `insert_archive_cve.py` and `insert_archive_cpe.py`

e.g.

Download and insert all versions of MITRE ATT&CK Enterprise

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti_knowledge_base_store \
	--ignore_embedded_relationships
```

Download specific versions of MITRE ATT&CK Enterprise and ignore embedded relationships

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti_knowledge_base_store \
	--versions 15_0,15_1
```