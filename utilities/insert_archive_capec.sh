#!/bin/bash
## LAST CHECKED 2024-06-01
## MITRE CAPEC
## version 3.5
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-capec/stix-capec-v3_5.json \
	--database cti \
	--collection mitre_capec \
	--stix2arango_note v3.5 \
	--ignore_embedded_relationships true \
&& \
## version 3.6
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-capec/stix-capec-v3_6.json \
	--database cti \
	--collection mitre_capec \
	--stix2arango_note v3.6 \
	--ignore_embedded_relationships true \
&& \
## version 3.7
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-capec/stix-capec-v3_7.json \
	--database cti \
	--collection mitre_capec \
	--stix2arango_note v3.7 \
	--ignore_embedded_relationships true \
&& \
## version 3.8
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-capec/stix-capec-v3_8.json \
	--database cti \
	--collection mitre_capec \
	--stix2arango_note v3.8 \
	--ignore_embedded_relationships true \
&& \
## version 3.9
python3 stix2arango.py \
	--file cti_knowledge_base_store/mitre-capec/stix-capec-v3_9.json \
	--database cti \
	--collection mitre_capec \
	--stix2arango_note v3.9 \
	--ignore_embedded_relationships true