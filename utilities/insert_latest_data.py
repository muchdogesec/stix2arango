import subprocess
import os
import requests

# Define the commands and their arguments for the initial files
commands = [
    {
        "file": "cti_knowledge_base_store/mitre-attack-enterprise/enterprise-attack-15_1.json",
        "database": "cti",
        "collection": "mitre_attack_enterprise",
        "stix2arango_note": "v15.1"
    },
    {
        "file": "cti_knowledge_base_store/mitre-attack-ics/ics-attack-15_1.json",
        "database": "cti",
        "collection": "mitre_attack_ics",
        "stix2arango_note": "v15.1"
    },
    {
        "file": "cti_knowledge_base_store/mitre-attack-mobile/mobile-attack-15_1.json",
        "database": "cti",
        "collection": "mitre_attack_mobile",
        "stix2arango_note": "v15.1"
    },
    {
        "file": "cti_knowledge_base_store/mitre-capec/stix-capec-v3_9.json",
        "database": "cti",
        "collection": "mitre_capec",
        "stix2arango_note": "v3.9"
    },
    {
        "file": "cti_knowledge_base_store/mitre-cwe/cwe-bundle-v4_14.json",
        "database": "cti",
        "collection": "mitre_cwe",
        "stix2arango_note": "v4.14"
    },
    {
        "file": "cti_knowledge_base_store/disarm/disarm-bundle-v1_4.json",
        "database": "cti",
        "collection": "disarm_framework",
        "stix2arango_note": "v1.4"
    },
    {
        "file": "cti_knowledge_base_store/sigma-rules/sigma-rule-bundle-r2024-05-13.json",
        "database": "cti",
        "collection": "sigma_rules",
        "stix2arango_note": "r2024-05-13"
    },
    {
        "file": "cti_knowledge_base_store/yara-rules/yara-rule-bundle-0f93570.json",
        "database": "cti",
        "collection": "yara_rules",
        "stix2arango_note": "0f93570"
    }
]

# List of CPE files
cpe_files = [
    "cpe-bundle-2007_07_01-2007_09_30.json",
    "cpe-bundle-2007_10_01-2007_12_31.json",
    "cpe-bundle-2008_01_01-2008_03_31.json",
    "cpe-bundle-2008_04_01-2008_06_30.json",
    "cpe-bundle-2008_07_01-2008_09_30.json",
    "cpe-bundle-2008_10_01-2008_12_31.json",
    "cpe-bundle-2009_01_01-2009_03_31.json",
    "cpe-bundle-2009_04_01-2009_06_30.json",
    "cpe-bundle-2009_07_01-2009_09_30.json",
    "cpe-bundle-2009_10_01-2009_12_31.json",
    "cpe-bundle-2010_01_01-2010_03_31.json",
    "cpe-bundle-2010_04_01-2010_06_30.json",
    "cpe-bundle-2010_07_01-2010_09_30.json",
    "cpe-bundle-2010_10_01-2010_12_31.json",
    "cpe-bundle-2011_01_01-2011_03_31.json",
    "cpe-bundle-2011_04_01-2011_06_30.json",
    "cpe-bundle-2011_07_01-2011_09_30.json",
    "cpe-bundle-2011_10_01-2011_12_31.json",
    "cpe-bundle-2012_01_01-2012_03_31.json",
    "cpe-bundle-2012_04_01-2012_06_30.json",
    "cpe-bundle-2012_07_01-2012_09_30.json",
    "cpe-bundle-2012_10_01-2012_12_31.json",
    "cpe-bundle-2013_01_01-2013_03_31.json",
    "cpe-bundle-2013_04_01-2013_06_30.json",
    "cpe-bundle-2013_07_01-2013_09_30.json",
    "cpe-bundle-2013_10_01-2013_12_31.json",
    "cpe-bundle-2014_01_01-2014_03_31.json",
    "cpe-bundle-2014_04_01-2014_06_30.json",
    "cpe-bundle-2014_07_01-2014_09_30.json",
    "cpe-bundle-2014_10_01-2014_12_31.json",
    "cpe-bundle-2015_01_01-2015_03_31.json",
    "cpe-bundle-2015_04_01-2015_06_30.json",
    "cpe-bundle-2015_07_01-2015_09_30.json",
    "cpe-bundle-2015_10_01-2015_12_31.json",
    "cpe-bundle-2016_01_01-2016_03_31.json",
    "cpe-bundle-2016_04_01-2016_06_30.json",
    "cpe-bundle-2016_07_01-2016_09_30.json",
    "cpe-bundle-2016_10_01-2016_12_31.json",
    "cpe-bundle-2017_01_01-2017_03_31.json",
    "cpe-bundle-2017_04_01-2017_06_30.json",
    "cpe-bundle-2017_07_01-2017_09_30.json",
    "cpe-bundle-2017_10_01-2017_12_31.json",
    "cpe-bundle-2018_01_01-2018_03_31.json",
    "cpe-bundle-2018_04_01-2018_06_30.json",
    "cpe-bundle-2018_07_01-2018_09_30.json",
    "cpe-bundle-2018_10_01-2018_12_31.json",
    "cpe-bundle-2019_01_01-2019_03_31.json",
    "cpe-bundle-2019_04_01-2019_06_30.json",
    "cpe-bundle-2019_07_01-2019_09_30.json",
    "cpe-bundle-2019_10_01-2019_12_31.json",
    "cpe-bundle-2020_01_01-2020_03_31.json",
    "cpe-bundle-2020_04_01-2020_06_30.json",
    "cpe-bundle-2020_07_01-2020_09_30.json",
    "cpe-bundle-2020_10_01-2020_12_31.json",
    "cpe-bundle-2021_01_01-2021_03_31.json",
    "cpe-bundle-2021_04_01-2021_06_30.json",
    "cpe-bundle-2021_07_01-2021_09_30.json",
    "cpe-bundle-2021_10_01-2021_12_31.json",
    "cpe-bundle-2022_01_01-2022_03_31.json",
    "cpe-bundle-2022_04_01-2022_06_30.json",
    "cpe-bundle-2022_07_01-2022_09_30.json",
    "cpe-bundle-2022_10_01-2022_12_31.json",
    "cpe-bundle-2023_01_01-2023_03_31.json",
    "cpe-bundle-2023_04_01-2023_06_30.json",
    "cpe-bundle-2023_07_01-2023_09_30.json",
    "cpe-bundle-2023_10_01-2023_12_31.json",
    "cpe-bundle-2024_01_01-2024_03_31.json"
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
    
    # Create necessary directories dynamically if they do not already exist
    for command in commands:
        directory = os.path.dirname(os.path.join(root_path, command["file"]))
        create_directory(directory)
    
    # Create directory for CPE files
    cpe_directory = os.path.join(root_path, "cti_knowledge_base_store", "nvd-cpe")
    create_directory(cpe_directory)
    
    # Download files
    base_url = "https://pub-ce0133952c6947428e077da707513ff5.r2.dev/"
    files_to_download = [
        {
            "url": f"{base_url}mitre-attack-enterprise%2Fenterprise-attack-15_1.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-attack-enterprise", "enterprise-attack-15_1.json")
        },
        {
            "url": f"{base_url}mitre-attack-ics%2Fics-attack-15_1.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-attack-ics", "ics-attack-15_1.json")
        },
        {
            "url": f"{base_url}mitre-attack-mobile%2Fmobile-attack-15_1.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-attack-mobile", "mobile-attack-15_1.json")
        },
        {
            "url": f"{base_url}disarm%2Fdisarm-bundle-v1_4.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "disarm", "disarm-bundle-v1_4.json")
        },
        {
            "url": f"{base_url}mitre-capec%2Fstix-capec-v3_9.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-capec", "stix-capec-v3_9.json")
        },
        {
            "url": f"{base_url}mitre-cwe%2Fcwe-bundle-v4_14.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "mitre-cwe", "cwe-bundle-v4_14.json")
        },
        {
            "url": f"{base_url}sigma-rules%2Fsigma-rule-bundle-r2024-05-13.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "sigma-rules", "sigma-rule-bundle-r2024-05-13.json")
        },
        {
            "url": f"{base_url}yara-rules%2Fyara-rule-bundle-0f93570.json",
            "destination": os.path.join(root_path, "cti_knowledge_base_store", "yara-rules", "yara-rule-bundle-0f93570.json")
        }
    ]

    for file in files_to_download:
        download_file(file["url"], file["destination"])

    # Download CPE files
    for cpe_file in cpe_files:
        url = f"{base_url}nvd-cpe%2F{cpe_file}"
        destination = os.path.join(root_path, "cti_knowledge_base_store", "nvd-cpe", cpe_file)
        download_file(url, destination)

    # Add CPE files to commands
    for cpe_file in cpe_files:
        commands.append({
            "file": f"cti_knowledge_base_store/nvd-cpe/{cpe_file}",
            "database": "cti",
            "collection": "nvd_cpe"
        })

    # Run the commands
    for command in commands:
        run_command(command, root_path)

if __name__ == "__main__":
    main()
