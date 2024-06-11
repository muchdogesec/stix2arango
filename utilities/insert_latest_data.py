import subprocess
import os
import requests
import time
import calendar
import argparse

# Define the commands and their arguments for the initial files
initial_commands = [
    {
        "file": "mitre-attack-enterprise/enterprise-attack-15_1.json",
        "database": "cti",
        "collection": "mitre_attack_enterprise",
        "stix2arango_note": "v15.1"
    },
    {
        "file": "mitre-attack-ics/ics-attack-15_1.json",
        "database": "cti",
        "collection": "mitre_attack_ics",
        "stix2arango_note": "v15.1"
    },
    {
        "file": "mitre-attack-mobile/mobile-attack-15_1.json",
        "database": "cti",
        "collection": "mitre_attack_mobile",
        "stix2arango_note": "v15.1"
    },
    {
        "file": "mitre-capec/stix-capec-v3_9.json",
        "database": "cti",
        "collection": "mitre_capec",
        "stix2arango_note": "v3.9"
    },
    {
        "file": "mitre-cwe/cwe-bundle-v4_14.json",
        "database": "cti",
        "collection": "mitre_cwe",
        "stix2arango_note": "v4.14"
    },
    {
        "file": "disarm/disarm-bundle-v1_4.json",
        "database": "cti",
        "collection": "disarm_framework",
        "stix2arango_note": "v1.4"
    },
    {
        "file": "sigma-rules/sigma-rule-bundle-r2024-05-13.json",
        "database": "cti",
        "collection": "sigma_rules",
        "stix2arango_note": "r2024-05-13"
    },
    {
        "file": "yara-rules/yara-rule-bundle-0f93570.json",
        "database": "cti",
        "collection": "yara_rules",
        "stix2arango_note": "0f93570"
    },
    {
        "file": "locations/locations-bundle.json",
        "database": "cti",
        "collection": "locations",
        "stix2arango_note": "2024-06-01"
    }
]

# List of CPE files
cpe_files = []
for year in range(2007, 2025):
    for quarter in range(1, 13, 3):
        start_month = quarter
        end_month = start_month + 2
        start_date = f"{year}_{str(start_month).zfill(2)}_01"
        end_day = calendar.monthrange(year, end_month)[1]
        end_date = f"{year}_{str(end_month).zfill(2)}_{str(end_day).zfill(2)}"
        cpe_files.append(f"cpe-bundle-{start_date}-{end_date}.json")

        # note you might see a few errors for earlier years b/c no data actually exists for these years. You can safely ignore them

# List of CVE files
cve_files = []
for year in range(2005, 2025):
    for month in range(1, 13):
        start_date = f"{year}_{str(month).zfill(2)}_01-00_00_00"
        end_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}_{str(month).zfill(2)}_{str(end_day).zfill(2)}-23_59_59"
        cve_files.append(f"cve-bundle-{start_date}-{end_date}.json")

        # note you might see a few errors for earlier years b/c no data actually exists for these years. You can safely ignore them

def create_directory(path):
    os.makedirs(path, exist_ok=True)
    print(f"Ensured directory exists: {path}")

def download_file(url, destination, error_list, max_retries=5, wait_time=60):
    retries = 0
    while retries < max_retries:
        if os.path.exists(destination):
            print(f"File already exists: {destination}")
            return
        response = requests.get(url)
        if response.status_code == 200:
            with open(destination, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded file to {destination}")
            return
        elif response.status_code == 429:
            retries += 1
            print(f"Rate limited. Retrying in {wait_time} seconds... (Attempt {retries} of {max_retries})")
            time.sleep(wait_time)
        else:
            error_list.append(f"Failed to download file from {url} with status code {response.status_code}")
            print(f"Failed to download file from {url} with status code {response.status_code}")
            return
    error_list.append(f"Failed to download file from {url} after {retries} attempts")
    print(f"Failed to download file from {url} after {retries} attempts")

def run_command(command, root_path):
    file_path = os.path.join(root_path, "cti_knowledge_base_store", command["file"])
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
    parser = argparse.ArgumentParser(description="Download and import certain collections")
    parser.add_argument('--collection', type=str, help='Specify the collection to download and import')
    args = parser.parse_args()

    # Get the absolute path to the ROOT directory (assumed to be the parent directory of the script)
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create necessary directories dynamically if they do not already exist
    all_commands = initial_commands.copy()

    # Define base URLs for downloads
    base_url = "https://pub-ce0133952c6947428e077da707513ff5.r2.dev/"
    paths = {
        "nvd-cpe": "nvd-cpe",
        "nvd-cve": "nvd-cve"
    }

    # List to store download errors
    download_errors = []

    # Function to add commands and download files
    def add_files(file_list, path_key, collection):
        create_directory(os.path.join(root_path, "cti_knowledge_base_store", path_key))
        for file_name in file_list:
            url = f"{base_url}{path_key}%2F{file_name}"
            destination = os.path.join(root_path, "cti_knowledge_base_store", path_key, file_name)
            download_file(url, destination, download_errors)
            all_commands.append({
                "file": f"{path_key}/{file_name}",
                "database": "cti",
                "collection": collection
            })

    # Filter commands if a specific collection is provided
    if args.collection:
        all_commands = [cmd for cmd in initial_commands if cmd["collection"] == args.collection]

    # Add CPE and CVE files to commands and download if no specific collection is provided
    if not args.collection or args.collection == "nvd_cpe":
        add_files(cpe_files, "nvd-cpe", "nvd_cpe")
    if not args.collection or args.collection == "nvd_cve":
        add_files(cve_files, "nvd-cve", "nvd_cve")

    # Download initial files
    for command in all_commands:
        if not args.collection or command["collection"] == args.collection:
            create_directory(os.path.join(root_path, "cti_knowledge_base_store", os.path.dirname(command["file"])))
            url = f"{base_url}{command['file'].replace('/', '%2F')}"
            download_file(url, os.path.join(root_path, "cti_knowledge_base_store", command["file"]), download_errors)

    # Run the commands
    for command in all_commands:
        run_command(command, root_path)

    # Print any download errors
    if download_errors:
        print("\nDownload Errors:")
        for error in download_errors:
            print(error)

if __name__ == "__main__":
    main()
