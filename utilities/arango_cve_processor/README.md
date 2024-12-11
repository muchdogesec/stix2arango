## arango_cve_processor

Downloads and imports files to ArangoDB used as the base data for arango_cve_processor.

To run these scripts, from the root of stix2arango;

```shell
python3 utilities/arango_cve_processor/SCRIPT
```

Where:

* `SCRIPT` (required): is either
	* `insert_archive_cve.py`
	* `insert_archive_cpe.py` (ARCHIVED -- logic now exists in [cpe2stix](https://github.com/muchdogesec/cpe2stix), and thus these objects are now imported via `insert_archive_cve.py`))
* `--database` (required): is the name of the Arango database the objects should be stored in. If database does not exist, stix2arango will create it
* `--ignore_embedded_relationships` (optional): boolean, if `True` passed, this will stop any embedded relationships from being generated. Default is `false`
* `--years` (optional): the years for which you want CPE and CVE data separated by a comma (e.g. `2024,2023)`. If no `years` flag is passed, all available years will be downloaded. IMPORTANT: flag only works with `insert_archive_cve.py` and `insert_archive_cpe.py`

e.g.

Download all CVE data

```shell
python3 utilities/arango_cve_processor/insert_archive_cve.py \
	--database cti_knowledge_base_store \
	--ignore_embedded_relationships True
```

Download only CVE data for year 2023 and 2024

```shell
python3 utilities/arango_cve_processor/insert_archive_cve.py \
	--database cti_knowledge_base_store \
	--years 2023,2024
```

#### A note on CVE and CPE data

You might see errors like this:

```txt
Failed to download file from https://downloads.ctibutler.com/cxe2stix-helper-github-action-output/cpe%2F2007-09%2Fcpe-bundle-2007_09_30-00_00_00-2007_09_30-23_59_59.json with status code 404
```

This is expected. It is expected because no data CPE/CVE exists between this time range, as such, no file exists and thus the download fails.

This is more of an issue when downloading all CVE or CPE data because in the earlier years large periods of time have no data (e.g. in 2007 there is no data until 2007-09).