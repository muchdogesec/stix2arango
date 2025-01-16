import argparse
import subprocess
import os
import requests
import time
import calendar
from datetime import datetime, timedelta
from stix2arango.stix2arango.stix2arango import Stix2Arango
from manager import VersionManager
from pathlib import Path


manager = VersionManager('utility_fails.db', 'cve_fails')

# Calculate the latest full year, month, and day
current_year = datetime.now().year
current_month = datetime.now().month
yesterday = datetime.now() - timedelta(days=1)
latest_year = yesterday.year
latest_month = yesterday.month
latest_day = yesterday.day

print(f"Latest full year: {latest_year}, Latest full month: {latest_month}, Latest full day: {latest_day}")

# List of CVE files with daily file names
all_versions = []
for year in range(1988, latest_year + 1):
    start_month = 1
    end_month = 12 if year < latest_year else latest_month
    for month in range(start_month, end_month + 1):
        days_in_month = calendar.monthrange(year, month)[1]
        if year == latest_year and month == latest_month:
            days_in_month = latest_day
        for day in range(1, days_in_month + 1):
            start_date = f"{year}_{str(month).zfill(2)}_{str(day).zfill(2)}"
            version = f"{start_date}-00_00_00-{start_date}-23_59_59"
            all_versions.append((year, month, version))

print("All versions to be processed:")
for item in all_versions:
    print(f"{item[0]}-{str(item[1]).zfill(2)}: {item[2]}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process NVD CVE versions.")
    parser.add_argument('--years', type=str, help='Comma-separated list of years to process. Default is all versions.')
    parser.add_argument('--ignore_embedded_relationships', action='store_true', help='Flag to ignore embedded relationships. Default is false.')
    parser.add_argument('--database', type=str, default="cti_knowledge_base_store", help='Name of the database to use. Default is "cti_knowledge_base_store".')
    parser.add_argument('--start_over', action='store_true', help='delete database holding whether previous attempts failed or not')
    return parser.parse_args()

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def download_file(version, url, destination, error_list, max_retries=5, wait_time=60):

    retries = 0
    exc = None
    while retries < max_retries:
        exc = None
        try:
            if os.path.exists(destination):
                print(f"File already exists: {destination}")
                return True
            response = requests.get(url)
            if response.status_code == 200:
                create_directory(os.path.dirname(destination))  # Ensure the directory exists before writing the file
                with open(destination, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded file to {destination}")
                return True
            elif response.status_code == 404:
                print(f"got 404 for {version}")
                manager.set_failed(version, False, reason="status: 404")
                return
            elif response.status_code == 400:
                #skipped
                return
            elif response.status_code == 429:
                retries += 1
                time.sleep(wait_time)
                raise Exception(f"Rate limited. Retrying in {wait_time} seconds... (Attempt {retries} of {max_retries})")
            else:
                error_list.append(f"Failed to download file from {url} with status code {response.status_code}")
                print(f"Failed to download file from {url} with status code {response.status_code}")
                break
        except Exception as e:
            exc = e
    manager.set_failed(version, True)
    error_list.append(f"Failed to download file from {url} after {retries} attempts: {exc}")
    print(f"Failed to download file from {url} after {retries} attempts")


def run_command(command, root_path, ignore_embedded_relationships):
    file_path = os.path.join(root_path, command["file"])
    stix2arango_path = os.path.join(root_path, "stix2arango.py")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    try:
        Stix2Arango(database=command["database"], collection=command["collection"], file=file_path, ignore_embedded_relationships=ignore_embedded_relationships).run()
        manager.set_failed(command['version'], failed=False, reason="uploaded to arango")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to process {file_path}: {e}")
        manager.set_failed(command['version'], failed=True, reason=str(e))

def main():
    args = parse_arguments()

    if args.years:
        selected_years = args.years.split(',')
        versions = [
            item for item in all_versions 
            if str(item[0]) in selected_years
        ]
    else:
        versions = all_versions

    if args.start_over:
        manager.recreate_table()
    new_versions = []
    failed_map = manager.get_versions()
    for item in versions:
        year, month, version = item
        if failed_map.get(version) in [True, None]:
            new_versions.append(item)

    print("will skip previously successful uploads")
    print(f"only {len(new_versions)} of {len(versions)} items will be processed")
    versions = new_versions

    ignore_embedded_relationships = args.ignore_embedded_relationships
    database = args.database

    # Get the absolute path to the current directory (where this script is located)
    script_path = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.abspath(os.path.join(script_path, "../.."))  # Move up two levels to the directory containing stix2arango.py and cti_knowledge_base_store
    
    # Define the commands and their arguments for the files
    commands = []
    
    # Download files
    base_url = "https://cve2stix.vulmatch.com/"
    download_errors = []

    for item in versions:
        year, month, version = item
        download_url = f"{base_url}{year}-{str(month).zfill(2)}/cve-bundle-{version}.json"
        destination_path = os.path.join(root_path, "cti_knowledge_base_store", f"nvd-cve/{year}-{str(month).zfill(2)}", f"cve-bundle-{version}.json")

        Path(destination_path).parent.mkdir(exist_ok=True, parents=True)

        if download_file(version, download_url, destination_path, download_errors):
            commands.append(dict(version=version, collection='nvd_cve', database=database, file=destination_path))

    # Run the commands
    for command in commands:
        # if command["version"] in manager.get_versions(failed=False):
        #     continue
        attempts = 0
        while attempts < 5:
            attempts += 1
            try:
                run_command(command, root_path, ignore_embedded_relationships)
            except Exception as e:
                print(e)
                continue

    # Print any download errors
    if download_errors:
        print("\nDownload Errors:")
        for error in download_errors:
            print(error)

if __name__ == "__main__":
    main()