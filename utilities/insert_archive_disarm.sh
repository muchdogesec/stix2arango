#!/bin/bash
## LAST CHECKED 2024-06-01
## DISARM Framwork
## version 1.2
python3 stix2arango.py \
	--file cti_knowledge_base_store/disarm/disarm-bundle-v1_2.json \
	--database cti \
	--collection disarm_framework \
	--stix2arango_note v1.2 \
	--ignore_embedded_relationships true \
&& \
## version 1.3
python3 stix2arango.py \
	--file cti_knowledge_base_store/disarm/disarm-bundle-v1_3.json \
	--database cti \
	--collection disarm_framework \
	--stix2arango_note v1.3 \
	--ignore_embedded_relationships true \
&& \
## version 1.4
python3 stix2arango.py \
	--file cti_knowledge_base_store/disarm/disarm-bundle-v1_4.json \
	--database cti \
	--collection disarm_framework \
	--stix2arango_note v1.4 \
	--ignore_embedded_relationships true