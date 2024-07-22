import argparse
from stix2arango.stix2arango import Stix2Arango

def parse_bool(value: str):
    value = value.lower()
    # ["false", "no", "n"]
    return value in ["yes", "y", "true", "1"]

def parse_arguments():
    parser = argparse.ArgumentParser(description="Import STIX JSON into ArangoDB")
    parser.add_argument("--file", required=True, help="Path to STIX JSON file")
    parser.add_argument("--database", required=True, help="ArangoDB database name")
    parser.add_argument("--collection", required=True, help="ArangoDB collection name")
    parser.add_argument("--stix2arango_note", required=False, help="Note for the import", default="")
    parser.add_argument("--ignore_embedded_relationships", required=False, help="Ignore Embedded Relationship for the import", type=parse_bool, default=False)

    return parser.parse_args()


def main():
    args = parse_arguments()
    print(args)
    stix_obj = Stix2Arango(args.database, args.collection, file=args.file, stix2arango_note=args.stix2arango_note, ignore_embedded_relationships=args.ignore_embedded_relationships)
    stix_obj.run()