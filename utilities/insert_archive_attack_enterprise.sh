#!/bin/bash
## LAST CHECKED 2024-06-01
## MITRE ATT&CK Enterprise
## version 1.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-1_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v1.0 \
	--ignore_embedded_relationships true \
&& \
## version 2.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-2_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v2.0 \
	--ignore_embedded_relationships true \
&& \
## version 3.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-3_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v3.0 \
	--ignore_embedded_relationships true \
&& \
## version 4.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-4_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v4.0 \
	--ignore_embedded_relationships true \
&& \
## version 5.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-5_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v5.0 \
	--ignore_embedded_relationships true \
&& \
## version 5.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-5_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v5.1 \
	--ignore_embedded_relationships true \
&& \
## version 5.2
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-5_2.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v5.2 \
	--ignore_embedded_relationships true \
&& \
## version 6.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-6_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v6.0 \
	--ignore_embedded_relationships true \
&& \
## version 6.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-6_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v6.1 \
	--ignore_embedded_relationships true \
&& \
## version 6.2
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-6_2.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v6.2 \
	--ignore_embedded_relationships true \
&& \
## version 6.3
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-6_3.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v6.3 \
	--ignore_embedded_relationships true \
&& \
## version 7.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-7_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v7.0 \
	--ignore_embedded_relationships true \
&& \
## version 7.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-7_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v7.1 \
	--ignore_embedded_relationships true \
&& \
## version 7.2
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-7_2.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v7.2 \
	--ignore_embedded_relationships true \
&& \
## version 8.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-8_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v8.0 \
	--ignore_embedded_relationships true \
&& \
## version 8.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-8_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v8.1 \
	--ignore_embedded_relationships true \
&& \
## version 8.2
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-8_2.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v8.2 \
	--ignore_embedded_relationships true \
&& \
## version 9.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-9_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v9.0 \
	--ignore_embedded_relationships true \
&& \
## version 10.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-10_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v10.0 \
	--ignore_embedded_relationships true \
&& \
## version 10.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-10_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v10.1 \
	--ignore_embedded_relationships true \
&& \
## version 11.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-11_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v11.0 \
	--ignore_embedded_relationships true \
&& \
## version 11.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-11_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v11.1 \
	--ignore_embedded_relationships true \
&& \
## version 11.2
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-11_2.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v11.2 \
	--ignore_embedded_relationships true \
&& \
## version 11.3
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-11_3.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v11.3 \
	--ignore_embedded_relationships true \
&& \
## version 12.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-12_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v12.0 \
	--ignore_embedded_relationships true \
&& \
## version 12.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-12_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v12.1 \
	--ignore_embedded_relationships true \
&& \
## version 13.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-13_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v13.0 \
	--ignore_embedded_relationships true \
&& \
## version 13.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-13_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v13.1 \
	--ignore_embedded_relationships true \
&& \
## version 14.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-v14_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v14.0 \
	--ignore_embedded_relationships true \
&& \
## version 14.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-14_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v14.1 \
	--ignore_embedded_relationships true \
&& \
## version 15.0
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-15_0.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v15.0 \
	--ignore_embedded_relationships true \
&& \
## version 15.1
python3 stix2arango.py \
    --file cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-15_1.json \
	--database cti \
	--collection mitre_attack_enterprise \
	--stix2arango_note v15.1 \
	--ignore_embedded_relationships true