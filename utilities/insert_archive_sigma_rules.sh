#!/bin/bash
## LAST CHECKED 2024-06-01
## Sigma Rules
## version r2023-08-24
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2023-08-24.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2023-08-24 \
	--ignore_embedded_relationships true \
&& \
## version r2023-10-09
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2023-10-09.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2023-10-09 \
	--ignore_embedded_relationships true \
&& \
## version r2023-10-23
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2023-10-23.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2023-10-23 \
	--ignore_embedded_relationships true \
&& \
## version r2023-11-06
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2023-11-06.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2023-11-06 \
	--ignore_embedded_relationships true \
&& \
## version r2023-11-20
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2023-11-20.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2023-11-20 \
	--ignore_embedded_relationships true \
&& \
## version r2023-12-04
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2023-12-04.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2023-12-04 \
	--ignore_embedded_relationships true \
&& \
## version r2023-12-21
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2023-12-21.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2023-12-21 \
	--ignore_embedded_relationships true \
&& \
## version r2024-01-15
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2024-01-15.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2024-01-15 \
	--ignore_embedded_relationships true \
&& \
## version r2024-01-29
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2024-01-29.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2024-01-29 \
	--ignore_embedded_relationships true \
&& \
## version r2024-02-12
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2024-02-12.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2024-02-12 \
	--ignore_embedded_relationships true \
&& \
## version r2024-02-26
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2024-02-26.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2024-02-26 \
	--ignore_embedded_relationships true \
&& \
## version r2024-03-11
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2024-03-11.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2024-03-11 \
	--ignore_embedded_relationships true \
&& \
## version r2024-03-26
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2024-03-26.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2024-03-26 \
	--ignore_embedded_relationships true \
&& \
## version r2024-04-29
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2024-04-29.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2024-04-29 \
	--ignore_embedded_relationships true \
&& \
## version r2024-05-13
python3 stix2arango.py \
	--file cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2024-05-13.json \
	--database cti \
	--collection sigma_rules \
	--stix2arango_note r2024-05-13 \
	--ignore_embedded_relationships true