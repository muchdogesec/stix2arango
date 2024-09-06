import argparse
import subprocess
import os
import requests
import time
import calendar
from datetime import datetime, timedelta

# Calculate the latest full year and month
current_year = datetime.now().year
current_month = datetime.now().month
yesterday = datetime.now() - timedelta(days=1)
latest_year = yesterday.year
latest_month = yesterday.month
latest_day = yesterday.day

print(f"Latest full year: {latest_year}, Latest full month: {latest_month}, Latest full day: {latest_day}")

# List of CVE files split by month or day depending on the date
all_versions = []
for year in range(2007, latest_year + 1):
    if year < 2024 or (year == 2024 and latest_month < 9):
        # Pre-September 2024 (Monthly files)
        start_month = 1
        end_month = 12 if year < latest_year else latest_month
        for month in range(start_month, end_month + 1):
            start_date = f"{year}_{str(month).zfill(2)}_01"
            end_day = calendar.monthrange(year, month)[1]
            if year == latest_year and month == latest_month:
                end_day = latest_day
            end_date = f"{year}_{str(month).zfill(2)}_{str(end_day).zfill(2)}"
            version = f"{start_date}-00_00_00-{end_date}-23_59_59"
            all_versions.append((year, version))
    elif year == 2024 and latest_month >= 9:
        # Post-September 2024 (Daily files)
        for month in range(1, 9):
            start_date = f"{year}_{str(month).zfill(2)}_01"
            end_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}_{str(month).zfill(2)}_{str(end_day).zfill(2)}"
            version = f"{start_date}-00_00_00-{end_date}-23_59_59"
            all_versions.append((year, version))
        for month in range(9, latest_month + 1):
            days_in_month = calendar.monthrange(year, month)[1]
            if year == latest_year and month == latest_month:
                days_in_month = latest_day
            for day in range(1, days_in_month + 1):
                start_date = f"{year}_{str(month).zfill(2)}_{str(day).zfill(2)}"
                version = f"{start_date}-00_00_00-{start_date}-23_59_59"
                all_versions.append((year, month, version))

print("All versions to be processed:")
for item in all_versions:
    if len(item) == 2:
        print(f"{item[0]}: {item[1]}")
    else:
        print(f"{item[0]}-{str(item[1]).zfill(2)}: {item[2]}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process NVD CVE versions.")
    parser.add_argument('--years', type=str, help='Comma-separated list of years to process. Default is all versions.')
    parser.add_argument('--ignore_embedded_relationships', type=bool, default=False, help='Flag to ignore embedded relationships. Default is false.')
    parser.add_argument('--database', type=str, default="cti", help='Name of the database to use. Default is "cti".')
    return parser.parse_args()

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def download_file(url, destination, error_list, max_retries=5, wait_time=60):
    retries = 0
    while retries < max_retries:
        if os.path.exists(destination):
            print(f"File already exists: {destination}")
            return
        response = requests.get(url)
        if response.status_code == 200:
            create_directory(os.path.dirname(destination))  # Ensure the directory exists before writing the file
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

    if args.years:
        selected_years = args.years.split(',')
        versions = [
            item for item in all_versions 
            if str(item[0]) in selected_years 
            and (len(item) == 2 or (item[0] == latest_year and item[1] <= latest_month))
        ]
    else:
        versions = all_versions

    ignore_embedded_relationships = args.ignore_embedded_relationships
    database = args.database

    # Get the absolute path to the current directory (where this script is located)
    script_path = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.abspath(os.path.join(script_path, "../.."))  # Move up two levels to the directory containing stix2arango.py and cti_knowledge_base_store
    
    # Define the commands and their arguments for the files
    commands = []
    for item in versions:
        if len(item) == 2:  # Pre-Sept 2024 format
            year, version = item
            file_path = os.path.join("cti_knowledge_base_store", "nvd-cve", str(year), f"cve-bundle-{version}.json")
        else:  # Post-Sept 2024 format
            year, month, version = item
            file_path = os.path.join("cti_knowledge_base_store", "nvd-cve", f"{year}-{str(month).zfill(2)}", f"cve-bundle-{version}.json")
        
        commands.append({
            "file": file_path,
            "database": database,
            "collection": "nvd_cve"
        })
    
    # Collect unique directories to create
    directories_to_create = set()
    for command in commands:
        directory = os.path.dirname(os.path.join(root_path, command["file"]))
        year_directory = os.path.dirname(directory)
        directories_to_create.add(year_directory)

        # Ensure the year-level directory is also added for pre-September 2024
        if len(command["file"].split('/')) == 4:  # This checks if it's the pre-Sept 2024 format
            directories_to_create.add(os.path.join(root_path, "cti_knowledge_base_store", "nvd-cve", str(year)))

        # Create the year-month-level directory (e.g., 2024-09) for post-September 2024 files
        directories_to_create.add(directory)
    
    # Create necessary directories dynamically if they do not already exist
    for directory in directories_to_create:
        create_directory(directory)
    
    # Download files
    base_url = "https://pub-4cfd2eaec94c4f6ea8b57724cccfca70.r2.dev/"
    files_to_download = []
    for item in versions:
        if len(item) == 2:  # Pre-Sept 2024 format
            year, version = item
            download_url = f"{base_url}cve%2F{year}%2Fcve-bundle-{version}.json"
            destination_path = os.path.join(root_path, "cti_knowledge_base_store", f"nvd-cve/{year}", f"cve-bundle-{version}.json")
        else:  # Post-Sept 2024 format
            year, month, version = item
            download_url = f"{base_url}cve%2F{year}-{str(month).zfill(2)}%2Fcve-bundle-{version}.json"
            destination_path = os.path.join(root_path, "cti_knowledge_base_store", f"nvd-cve/{year}-{str(month).zfill(2)}", f"cve-bundle-{version}.json")
        
        files_to_download.append({
            "url": download_url,
            "destination": destination_path
        })

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
