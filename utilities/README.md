## stix2arango utilities

### arango_cti_processor

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
	* `insert_archive_capecv`
	* `insert_archive_cpe.py`
	* `insert_archive_cve.py`
	* `insert_archive_cwe.py`
	* `insert_archive_disarm.py`
	* `insert_archive_location.py`
	* `insert_archive_sigma_rules.py`
	* `insert_archive_yara_rules.py`
	* `insert_archive_tlp.py`
	
* `--database` (required): is the name of the Arango database the objects should be stored in. If database does not exist, stix2arango will create it
* `--ignore_embedded_relationships` (optional): boolean, if `true` passed, this will stop any embedded relationships from being generated. Default is `false`
* `--versions` (optional): are one or more of the versions listed in each script. e.g. for `insert_archive_disarm.py` are currently `1_2`, `1_3`, `1_4`. If no `version` flag is passed, all listed versions will be downloaded. IMPORTANT: flag does not work with `insert_archive_cve.py` and `insert_archive_cpe.py`
* `--years` (optional): the years for which you want CPE and CVE data separated by a comma (e.g. `2024,2023)`. If no `years` flag is passed, all available years will be downloaded. IMPORTANT: flag only works with `insert_archive_cve.py` and `insert_archive_cpe.py`

e.g.

Download and insert all versions of MITRE ATT&CK Enterprise

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti_knowledge_base_store
```

Download specific versions of MITRE ATT&CK Enterprise and ignore embedded relationships

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti_knowledge_base_store \
	--versions 15_0,15_1
```

Download all CVE data

```shell
python3 utilities/arango_cti_processor/insert_archive_cve.py \
	--database cti_knowledge_base_store
```

Download only CVE data for year 2023 and 2024

```shell
python3 utilities/arango_cti_processor/insert_archive_cve.py \
	--database cti_knowledge_base_store \
	--years 2023,2024
```

You can see the full commands we use to import data to arango_cti_processor here: https://github.com/muchdogesec/arango_cti_processor/tree/main/examples

#### A note on CVE and CPE data

You might see errors like this:

```txt
Failed to download file from https://downloads.ctibutler.com/cxe2stix-helper-github-action-output/cpe%2F2007-09%2Fcpe-bundle-2007_09_30-00_00_00-2007_09_30-23_59_59.json with status code 404
```

This is expected. It is expected because no data CPE/CVE exists between this time range, as such, no file exists and thus the download fails.

This is more of an issue when downloading all CVE or CPE data because in the earlier years large periods of time have no data (e.g. in 2007 there is no data until 2007-09).

#### Quick-start

Download all versions, and create embedded relationships;

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_attack_ics.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_attack_mobile.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_capec.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_cwe.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_sigma_rules.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_cve.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_cpe.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_disarm.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_locations.py \
  --database cti_knowledge_base_store && \
python3 utilities/arango_cti_processor/insert_archive_yara_rules.py \
  --database cti_knowledge_base_store
```