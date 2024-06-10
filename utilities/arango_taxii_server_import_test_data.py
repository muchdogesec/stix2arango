import subprocess
import os
import requests
import re

# Define the version strings for each category
enterprise_versions = [
    "14_1", "15_0", "15_1"
]
ics_versions = [
    "14_1", "15_0", "15_1"
]
mobile_versions = [
    "14_1", "15_0", "15_1"
]

# Sort the versions
enterprise_versions.sort(key=lambda x: list(map(int, x.split('_'))))
ics_versions.sort(key=lambda x: list(map(int, x.split('_'))))
mobile_versions.sort(key=lambda x: re.split(r'[_-]', x))

# Define the commands and their arguments for the files
commands = [
    {
        "file": f"cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-{version}.json",
        "database": "arango_taxii_server_tests",
        "collection": "mitre_attack_enterprise",
        "stix2arango_note": f"v{version.replace('_', '.')}"
    } for version in enterprise_versions
] + [
    {
        "file": f"cti_knowledge_base_store/mitre-attack-ics/ics-attack-{version}.json",
        "database": "arango_taxii_server_tests",
        "collection": "mitre_attack_ics",
        "stix2arango_note": f"v{version.replace('_', '.')}"
    } for version in ics_versions
] + [
    {
        "file": f"cti_knowledge_base_store/mitre-attack-mobile/mobile-attack-{version}.json",
        "database": "arango_taxii_server_tests",
        "collection": "mitre_attack_mobile",
        "stix2arango_note": f"v{version.replace('_', '.')}"
    } for version in mobile_versions
]

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

def run_command(command, root_path):
    file_path = os.path.join(root_path, command["file"])
    stix2arango_path = os.path.join(root_path, "stix2arango.py")
    stix2arango_dir = os.path.dirname(stix2arango_path)  # Directory containing stix2arango.py
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    if not os.path.exists(stix2arango_path):
        print(f"stix2arango.py not found: {stix2arango_path}")
        return
    try:
        # Change the working directory to the directory containing stix2arango.py
        subprocess.run([
            "python3", stix2arango_path,
            "--file", file_path,
            "--database", command["database"],
            "--collection", command["collection"],
            "--stix2arango_note", command.get("stix2arango_note", ""),
            "--ignore_embedded_relationships", "true"
        ], check=True, cwd=stix2arango_dir)
        print(f"Successfully processed {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to process {file_path}: {e}")

def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f"Removed file: {file_path}")
    except OSError as e:
        print(f"Error removing file {file_path}: {e}")

def main():
    # Get the absolute path to the ROOT directory (assumed to be the parent directory of the script)
    root_path = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(root_path)  # Move up one level from 'utilities' to 'ROOT'
    
    # Collect unique directories to create
    directories_to_create = set()
    for command in commands:
        directory = os.path.dirname(os.path.join(root_path, command["file"]))
        directories_to_create.add(directory)
    
    # Create necessary directories dynamically if they do not already exist
    for directory in directories_to_create:
        create_directory(directory)
    
    # Download files
    base_url = "https://pub-ce0133952c6947428e077da707513ff5.r2.dev/"
    files_to_download = [
        {
            "url": f"{base_url}mitre-attack-enterprise%2Fenterprise-attack-{version}.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-attack-enterprise", f"enterprise-attack-{version}.json")
        } for version in enterprise_versions
    ] + [
        {
            "url": f"{base_url}mitre-attack-ics%2Fics-attack-{version}.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-attack-ics", f"ics-attack-{version}.json")
        } for version in ics_versions
    ] + [
        {
            "url": f"{base_url}mitre-attack-mobile%2Fmobile-attack-{version}.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-attack-mobile", f"mobile-attack-{version}.json")
        } for version in mobile_versions
    ]

    for file in files_to_download:
        download_file(file["url"], file["destination"])

    # Run the commands
    for command in commands:
        run_command(command, root_path)

if __name__ == "__main__":
    main()
