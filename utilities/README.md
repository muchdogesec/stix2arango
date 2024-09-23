## stix2arango utilities

### arango_cti_processor

Downloads and imports files to ArangoDB used as the base data for arango_cti_processor.

To run these scripts, from the root of stix2arango;

```shell
python3 utilities/arango_cti_processor/SCRIPT.py
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
	* `insert_archive_location`
	* `insert_archive_sigma_rules`
	* `insert_archive_yara_rules`
	
* `--database` (required): is the name of the Arango database the objects should be stored in. If database does not exist, stix2arango will create it
* `--ignore_embedded_relationships` (optional): boolean, if `true` passed, this will stop any embedded relationships from being generated. Default is `false`
* `--versions` (optional): are one or more of the versions listed in each script. e.g. for `insert_archive_disarm.py` are currently `1_2`, `1_3`, `1_4`. If no `version` flag is passed, all listed versions will be downloaded. IMPORTANT: flag does not work with `insert_archive_cve.py` and `insert_archive_cpe.py`
* `--years` (optional): the years for which you want CPE and CVE data separated by a comma (e.g. `2024,2023)`. If no `years` flag is passed, all available years will be downloaded. IMPORTANT: flag only works with `insert_archive_cve.py` and `insert_archive_cpe.py`

e.g.

Download and insert all versions of MITRE ATT&CK Enterprise

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti
```

Download specific versions of MITRE ATT&CK Enterprise and ignore embedded relationships

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti \
	--versions 15_0,15_1
```

Download all CVE data

```shell
python3 utilities/arango_cti_processor/insert_archive_cve.py \
	--database cti
```

Download only CVE data for year 2023 and 2024

```shell
python3 utilities/arango_cti_processor/insert_archive_cve.py \
	--database cti \
	--years 2023,2024
```

You can see the full commands we use to import data to arango_cti_processor here: https://github.com/muchdogesec/arango_cti_processor/tree/main/examples

#### A note on CVE and CPE data

You might see errors like this:

```txt
Download Errors:
Failed to download file from https://pub-4cfd2eaec94c4f6ea8b57724cccfca70.r2.dev/cpe%2F2007%2Fcpe-bundle-2007_01_01-00_00_00-2007_01_31-23_59_59.json with status code 404
```

This is expected. It is expected because no data CPE/CVE exists between this time range, as such, no file exists and thus the download fails.