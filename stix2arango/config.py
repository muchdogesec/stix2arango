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