## stix2arango utilities

### arango_cti_processor

Downloads and imports files to ArangoDB used as the base data for arango_cti_processor.

To run these scripts, from the root of stix2arango;

```shell
python3 utilities/arango_cti_processor/SCRIPT.py --versions XX,YY,ZZ
```

Where:

* `SCRIPT` (required): is either
	* `insert_archive_attack_enterprise`
	* `insert_archive_attack_ics`
	* `insert_archive_attack_mobile`
	* `insert_archive_capec`
	* `insert_archive_cpe`
	* `insert_archive_cve`
	* `insert_archive_cwe`
	* `insert_archive_disarm`
	* `insert_archive_locations`
	* `insert_archive_sigma_rules`
	* `insert_archive_yara_rules`
	
* `--database` (required): is the name of the Arango database the objects should be stored in. If database does not exist, stix2arango will create it
* `--versions` (optional): are one or more of the versions listed in each Python file. e.g. for `insert_archive_disarm.py` are currently `1_2`, `1_3`, `1_4`. If no version flag is passed, all listed versions will be downloaded. 
* `--ignore_embedded_relationships` (optional): boolean, if `true` passed, this will stop any embedded relationships from being generated. Default is `false`

e.g.

Download and insert all versions of MITRE ATT&CK Enterprise

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti
```

Download and insert all data (what we use when spinning up a new arango_cti_processor install):

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_attack_ics.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_attack_mobile.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_capec.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_cpe.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_cve.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_cwe.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_disarm.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_locations.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_sigma_rules.py \
	--database cti && \
python3 utilities/arango_cti_processor/insert_archive_yara_rules.py \
	--database cti && \
```

Download and insert only 15.0 and 15.1 versions of MITRE ATT&CK Enterprise and ignore embedded relationships

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py --database cti --versions 15_0,15_1 --ignore_embedded_relationships true
```