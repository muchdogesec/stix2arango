#!/bin/bash
## LAST CHECKED 2024-06-01
## MITRE ATT&CK ICS
## version 8.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-8_0.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v8.0 \
	--ignore_embedded_relationships true \
&& \
## version 8.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-8_1.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v8.1 \
	--ignore_embedded_relationships true \
&& \
## version 8.2
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-8_2.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v8.2 \
	--ignore_embedded_relationships true \
&& \
## version 9.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-9_0.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v9.0 \
	--ignore_embedded_relationships true \
&& \
## version 10.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-10_0.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v10.0 \
	--ignore_embedded_relationships true \
&& \
## version 10.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-10_1.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v10.1 \
	--ignore_embedded_relationships true \
&& \
## version 11.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-11_0.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v11.0 \
	--ignore_embedded_relationships true \
&& \
## version 11.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-11_1.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v11.1 \
	--ignore_embedded_relationships true \
&& \
## version 11.2
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-11_2.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v11.2 \
	--ignore_embedded_relationships true \
&& \
## version 11.3
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-11_3.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v11.3 \
	--ignore_embedded_relationships true \
&& \
## version 12.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-12_0.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v12.0 \
	--ignore_embedded_relationships true \
&& \
## version 12.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-12_1.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v12.1 \
	--ignore_embedded_relationships true \
&& \
## version 13.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-13_0.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v13.0 \
	--ignore_embedded_relationships true \
&& \
## version 13.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-13_1.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v13.1 \
	--ignore_embedded_relationships true \
&& \
## version 14.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-v14_0.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v14.0 \
	--ignore_embedded_relationships true \
&& \
## version 14.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-14_1.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v14.1 \
	--ignore_embedded_relationships true \
&& \
## version 15.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-15_0.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v15.0 \
	--ignore_embedded_relationships true \
&& \
## version 15.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-ics/ics-attack-15_1.json \
	--database cti \
	--collection mitre_attack_ics \
	--stix2arango_note v15.1 \
	--ignore_embedded_relationships true