import subprocess
import os
import requests
import re

# Define the version strings
versions = [
    "2023-08-24", "2023-10-09", "2023-10-23", "2023-11-06", "2023-11-20", "2023-12-04",
    "2023-12-21", "2024-01-15", "2024-01-29", "2024-02-12", "2024-02-26", "2024-03-11",
    "2024-03-26", "2024-04-29", "2024-05-13"
]

def version_key(version):
    parts = re.split(r'[_-]', version)
    return [int(part) if part.isdigit() else part for part in parts]

# Sort the versions using the custom key
versions.sort(key=version_key)

# Define the commands and their arguments for the files
commands = [
    {
        "file": f"cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r{version}.json",
        "database": "cti",
        "collection": "sigma_rules",
        "stix2arango_note": f"v{version.replace('_', '.')}"
    } for version in versions
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
            "--ignore_embedded_relationships", "true"
        ], check=True)
        print(f"Successfully processed {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to process {file_path}: {e}")

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
            "url": f"{base_url}sigma-rules%2Fsigma-rule-bundle-r{version}.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "sigma-rules", f"sigma-rule-bundle-r{version}.json")
        } for version in versions
    ]

    for file in files_to_download:
        download_file(file["url"], file["destination"])

    # Run the commands
    for command in commands:
        run_command(command, root_path)

if __name__ == "__main__":
    main()
