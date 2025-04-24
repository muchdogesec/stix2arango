import argparse
import subprocess
import os
import requests

# Define the version strings
all_versions = [
    "4_9_0"
]

# Sort the versions
all_versions.sort(key=lambda x: list(map(int, x.split('_'))))

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process MITRE ATT&CK versions.")
    parser.add_argument('--versions', type=str, help='Comma-separated list of versions to process (e.g., 1_0,2_0). Default is all versions.')
    parser.add_argument('--ignore_embedded_relationships', action='store_true', help='Flag to ignore embedded relationships. Default is false.')
    parser.add_argument('--database', type=str, default="cti_knowledge_base_store", help='Name of the database to use. Default is "cti".')
    return parser.parse_args()

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def download_file(url, destination):
    if os.path.exists(destination):
        print(f"File already exists: {destination}")
        return
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded file to {destination}")
    else:
        print(f"Failed to download file from {url}")

def run_command(command, root_path, ignore_embedded_relationships):
    file_path = os.path.join(root_path, command["file"])
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    try:
        subprocess.run([
            "python3", os.path.join(root_path, "stix2arango.py"),
            "--file", file_path,
            "--database", command["database"],
            "--collection", command["collection"],
            "--stix2arango_note", command.get("stix2arango_note", ""),
            "--ignore_embedded_relationships", str(ignore_embedded_relationships)
        ], check=True)
        print(f"Successfully processed {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to process {file_path}: {e}")

def main():
    args = parse_arguments()

    if args.versions:
        versions = args.versions.split(',')
    else:
        versions = all_versions

    ignore_embedded_relationships = args.ignore_embedded_relationships
    database = args.database

    # Get the absolute path to the current directory (where this script is located)
    script_path = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.abspath(os.path.join(script_path, "../.."))  # Move up two levels to the directory containing stix2arango.py and cti_knowledge_base_store
    
    # Define the commands and their arguments for the files
    commands = [
        {
            "file": os.path.join("cti_knowledge_base_store", "mitre-atlas", f"mitre-atlas-v{version}.json"),
            "database": database,
            "collection": "mitre_atlas",
            "stix2arango_note": f"v{version.replace('_', '.')}"
        } for version in versions
    ]
    
    # Collect unique directories to create
    directories_to_create = set()
    for command in commands:
        directory = os.path.dirname(os.path.join(root_path, command["file"]))
        directories_to_create.add(directory)
    
    # Create necessary directories dynamically if they do not already exist
    for directory in directories_to_create:
        create_directory(directory)
    
    # Download files
    base_url = "https://downloads.ctibutler.com/"
    files_to_download = [
        {
            "url": f"{base_url}mitre-atlas-repo-data/mitre-atlas-v{version}.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-atlas", f"mitre-atlas-v{version}.json")
        } for version in versions
    ]

    for file in files_to_download:
        download_file(file["url"], file["destination"])

    # Run the commands
    for command in commands:
        run_command(command, root_path, ignore_embedded_relationships)

if __name__ == "__main__":
    main()
