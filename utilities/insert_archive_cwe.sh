#!/bin/bash
## LAST CHECKED 2024-06-01
## MITRE CWE
## version 4.5
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_5.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.5 \
	--ignore_embedded_relationships true \
&& \
## version 4.6
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_6.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.6 \
	--ignore_embedded_relationships true \
&& \
## version 4.7
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_7.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.7 \
	--ignore_embedded_relationships true \
&& \
## version 4.8
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_8.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.8 \
	--ignore_embedded_relationships true \
&& \
## version 4.9
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_9.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.9 \
	--ignore_embedded_relationships true \
&& \
## version 4.10
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_10.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.10 \
	--ignore_embedded_relationships true \
&& \
## version 4.11
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_11.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.11 \
	--ignore_embedded_relationships true \
&& \
## version 4.12
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_12.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.12 \
	--ignore_embedded_relationships true \
&& \
## version 4.13
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_13.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.13 \
	--ignore_embedded_relationships true \
&& \
## version 4.14
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_14.json \
	--database cti \
	--collection mitre_cwe \
	--stix2arango_note v4.14 \
	--ignore_embedded_relationships true