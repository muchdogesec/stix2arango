import subprocess
import os
import requests

# Define the version strings
versions = [
    "8_0", "8_1", "8_2", "9_0", "10_0", "10_1", "11_0", 
    "11_1", "11_2", "11_3", "12_0", "12_1", "13_0", "13_1", "14_0", "14_1", 
    "15_0", "15_1"
]

# Sort the versions
versions.sort(key=lambda x: list(map(int, x.split('_'))))

# Define the commands and their arguments for the files
commands = [
    {
        "file": f"cti_knowledge_base_store/mitre-attack-ics/ics-attack-{version}.json",
        "database": "cti",
        "collection": "mitre_attack_ics",
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
            "--ignore_embedded_relationships", "false"
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
            "url": f"{base_url}mitre-attack-ics%2Fics-attack-{version}.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-attack-ics", f"ics-attack-{version}.json")
        } for version in versions
    ]

    for file in files_to_download:
        download_file(file["url"], file["destination"])

    # Run the commands
    for command in commands:
        run_command(command, root_path)

if __name__ == "__main__":
    main()
