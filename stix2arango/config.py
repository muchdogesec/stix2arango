import os
import logging
from dotenv import load_dotenv
from uuid import UUID

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",  # noqa D100 E501
    datefmt="%Y-%m-%d - %H:%M:%S",
)
ARANGODB_HOST = os.getenv("ARANGODB_HOST")
ARANGODB_PORT = os.getenv("ARANGODB_PORT")
ARANGODB_USERNAME = os.getenv("ARANGODB_USERNAME")
ARANGODB_PASSWORD = os.getenv("ARANGODB_PASSWORD")

json_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "const": "bundle"},
        "id": {"type": "string"},
        "objects": {"type": "array", "items": {"type": "object"}}
    },
    "required": ["type", "id", "objects"]
}
STIX2ARANGO_IDENTITY = "https://github.com/muchdogesec/stix4doge/raw/main/objects/identity/stix2arango.json" # this is stix2arango identity
DOGESEC_IDENTITY = "https://github.com/muchdogesec/stix4doge/raw/main/objects/identity/dogesec.json" # this is stix2arango identity

STIX2ARANGO_MARKING_DEFINITION = "https://raw.githubusercontent.com/muchdogesec/stix4doge/main/objects/marking-definition/stix2arango.json" # this is stix2arango marking-definition

IDENTITY_REFS = [
    STIX2ARANGO_IDENTITY,
    DOGESEC_IDENTITY
]
MARKING_DEFINITION_REFS = [
   STIX2ARANGO_MARKING_DEFINITION
]
DEFAULT_OBJECT_URL = MARKING_DEFINITION_REFS + IDENTITY_REFS

namespace = UUID("72e906ce-ca1b-5d73-adcd-9ea9eb66a1b4")

refs_list = [
            # default objects from STIX spec
            "analysis_sco_refs",
            "bcc_refs",
            "belongs_to_refs",
            "cc_refs",
            "child_refs",
            "contains_refs",
            "encapsulates_refs",
            "installed_software_refs",
            "object_marking_refs",
            "object_refs",
            "observed_data_refs",
            "opened_connection_refs",
            "resolves_to_refs",
            "sample_refs",
            "service_dll_refs",
            "to_refs","where_sighted_refs",
            "body_raw_ref",
            "created_by_ref",
            "creator_user_ref",
            "dst_payload_ref",
            "dst_ref",
            "encapsulated_by_ref",
            "from_ref",
            "host_vm_ref",
            "image_ref",
            "marking_ref",
            "object_ref",
            "operating_system_ref",
            "parent_directory_ref",
            "parent_ref",
            "raw_email_ref",
            "sample_ref",
            "sender_ref",
            "sighting_of_ref",
            "src_payload_ref",
            "src_ref",
            # MITRE CAPEC custom ref properties
            "x_capec_parent_of_refs",
            "x_capec_child_of_refs",
            "x_capec_can_precede_refs",
            "x_capec_can_follow_refs",
            # MITRE ATT&CK custom properties
            "tactic_refs",
            "x_mitre_modified_by_ref"
            ]