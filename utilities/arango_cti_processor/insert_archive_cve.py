import argparse
import subprocess
import os
import requests
import time
import calendar
from datetime import datetime

# Calculate the last full month
current_year = datetime.now().year
current_month = datetime.now().month

if current_month == 1:
    last_full_month_year = current_year - 1
    last_full_month = 12
else:
    last_full_month_year = current_year
    last_full_month = current_month - 1

print(f"Last full month: {last_full_month_year}-{str(last_full_month).zfill(2)}")

# List of CVE files
all_versions = []
missing_files = [
    "2005_10", "2007_07", "2008_09", "2008_10", "2008_11", "2008_12", "2009_01"
]

# Add missing files
for entry in missing_files:
    year, month = map(int, entry.split('_'))
    start_date = f"{year}_{str(month).zfill(2)}_01-00_00_00"
    end_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}_{str(month).zfill(2)}_{str(end_day).zfill(2)}-23_59_59"
    all_versions.append(f"{start_date}-{end_date}")

# Add all months from 2009 onwards up to the last full month
for year in range(2009, last_full_month_year + 1):
    start_month = 1
    end_month = 12 if year < last_full_month_year else last_full_month
    for month in range(start_month, end_month + 1):
        start_date = f"{year}_{str(month).zfill(2)}_01-00_00_00"
        end_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}_{str(month).zfill(2)}_{str(end_day).zfill(2)}-23_59_59"
        all_versions.append(f"{start_date}-{end_date}")

print("All versions to be processed:")
for version in all_versions:
    print(version)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process NVD CVE versions.")
    parser.add_argument('--versions', type=str, help='Comma-separated list of versions to process (e.g., 2023_08_24-00_00_00,2023_10_09-00_00_00). Default is all versions.')
    parser.add_argument('--ignore_embedded_relationships', type=bool, default=False, help='Flag to ignore embedded relationships. Default is false.')
    parser.add_argument('--database', type=str, default="cti", help='Name of the database to use. Default is "cti".')
    return parser.parse_args()

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

def run_command(command, root_path, ignore_embedded_relationships):
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
            "--ignore_embedded_relationships", str(ignore_embedded_relationships).lower()
        ], check=True, cwd=stix2arango_dir)
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
            "file": os.path.join("cti_knowledge_base_store", "nvd-cve", f"cve-bundle-{version}.json"),
            "database": database,
            "collection": "nvd_cve"
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
    base_url = "https://pub-ce0133952c6947428e077da707513ff5.r2.dev/"
    files_to_download = [
        {
            "url": f"{base_url}nvd-cve%2Fcve-bundle-{version}.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "nvd-cve", f"cve-bundle-{version}.json")
        } for version in versions
    ]

    download_errors = []

    for file in files_to_download:
        download_file(file["url"], file["destination"], download_errors)

    # Run the commands
    for command in commands:
        run_command(command, root_path, ignore_embedded_relationships)

    # Print any download errors
    if download_errors:
        print("\nDownload Errors:")
        for error in download_errors:
            print(error)

if __name__ == "__main__":
    main()
