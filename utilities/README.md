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
	* `insert_archive_locations`
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
	--database cti \
	--ignore_embedded_relationships false
```

Download specific versions of MITRE ATT&CK Enterprise and ignore embedded relationships

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti \
	--ignore_embedded_relationships false \
	--versions 15_0,15_1
```

Download all CVE data

```shell
python3 utilities/arango_cti_processor/insert_archive_cve.py \
	--database cti \
	--ignore_embedded_relationships false
```

Download only CVE data for year 2023 and 2024

```shell
python3 utilities/arango_cti_processor/insert_archive_cve.py \
	--database cti \
	--ignore_embedded_relationships false \
	--years 2023,2024
```

If you just want the latest data (at the time of writing), this command will give you what you need;

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py \
	--database cti \
	--versions 15_1 \
    --ignore_embedded_relationships true && \
python3 utilities/arango_cti_processor/insert_archive_attack_ics.py \
	--database cti \
	--versions 15_1 \
    --ignore_embedded_relationships true && \
python3 utilities/arango_cti_processor/insert_archive_attack_mobile.py \
	--database cti \
	--versions 15_1 \
    --ignore_embedded_relationships true && \
python3 utilities/arango_cti_processor/insert_archive_capec.py \
	--database cti \
	--versions 3_9 \
    --ignore_embedded_relationships true && \
python3 utilities/arango_cti_processor/insert_archive_cwe.py \
	--database cti \
	--versions 4_14 \
    --ignore_embedded_relationships true && \
python3 utilities/arango_cti_processor/insert_archive_disarm.py \
	--database cti \
	--versions 1_4 \
    --ignore_embedded_relationships true && \
python3 utilities/arango_cti_processor/insert_archive_locations.py \
	--database cti \
    --ignore_embedded_relationships true && \
python3 utilities/arango_cti_processor/insert_archive_sigma_rules.py \
	--database cti \
	--versions 2024-07-17 \
    --ignore_embedded_relationships true && \
python3 utilities/arango_cti_processor/insert_archive_yara_rules.py \
	--database cti \
	--versions 0f93570 \
    --ignore_embedded_relationships true && \
python3 utilities/arango_cti_processor/insert_archive_cve.py \
	--database cti \
	--ignore_embedded_relationships false \
	--years 2017,2018,2019,2020,2021,2022,2023,2024 && \
python3 utilities/arango_cti_processor/insert_archive_cpe.py \
	--database cti \
	--ignore_embedded_relationships false
```

Note, old products are often referenced in CVEs, so to be safe, all CPE data is downloaded.

CVEs are downloaded from 2017, as this is the earliest CVE year referenced in a Sigma rule.