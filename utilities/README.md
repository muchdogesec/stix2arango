## stix2arango utilities

### arango_cti_processor

Downloads and imports files to ArangoDB used as the base data for arango_cti_processor.

To run these scripts, from the root of stix2arango;

```shell
python3 utilities/arango_cti_processor/SCRIPT.py --versions XX,YY,ZZ
```

Where:

* `SCRIPT` (required): is either
	* `mitre_attack_enterprise`
	* `mitre_attack_ics`
	* `mitre_attack_mobile`
	* `mitre_capec`
	* `mitre_cwe`
	* `nvd_cve`
	* `nvd_cpe`
	* `sigma-rules`
	* `yara-rules`
	* `locations`
* `--database` (required): is the name of the Arango database the objects should be stored in. If database does not exist, stix2arango will create it
* `--versions` (optional): are one or more of the versions listed in each Python file. e.g. for `insert_archive_disarm.py` are currently `1_2`, `1_3`, `1_4`. If no version flag is passed, all listed versions will be downloaded. 
* `--ignore_embedded_relationships` (optional): boolean, if `true` passed, this will stop any embedded relationships from being generated. Default is `false`

e.g.

Download and insert all versions of MITRE ATT&CK Enterprise

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py
```

Download and insert only 15.0 and 15.1 versions of MITRE ATT&CK Enterprise and ignore embedded relationships

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py --database cti --versions 15_0,15_1 --ignore_embedded_relationships true
```

For arango_cti_processor we run the following;

```shell
python3 utilities/arango_cti_processor/insert_archive_attack_enterprise.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_attack_ics.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_attack_mobile.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_capec.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_cwe.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_disarm.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_locations.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_sigma_rules.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_yara_rules.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_cve.py --database cti --ignore_embedded_relationships false && \
python3 utilities/arango_cti_processor/insert_archive_cpe.py --database cti --ignore_embedded_relationships false
```

IMPORTANT NOTE on CPE / CVE scripts: due to the way dates are generated dynamically you will see alot of errors like

```txt
ailed to download file from https://pub-ce0133952c6947428e077da707513ff5.r2.dev/nvd-cve%2Fcve-bundle-2007_11_01-00_00_00-2007_11_30-23_59_59.json with status code 404
```

This is normal. These files don't exist (as there is no data for these periods), however the script has been built in a dumb way to iterate through all possible data hence these errors.