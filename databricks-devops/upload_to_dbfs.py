# cicd-script/upload_to_dbfs.py

import os
import requests
import argparse

def upload_file_to_dbfs(databricks_instance, databricks_token, local_file_path, dbfs_file_path):
    url = f"https://{databricks_instance}/api/2.0/dbfs/put"
    headers = {
        "Authorization": f"Bearer {databricks_token}"
    }
    with open(local_file_path, 'rb') as f:
        data = f.read()
    json_payload = {
        "path": dbfs_file_path,
        "overwrite": True
    }
    files = {
        'contents': data
    }
    response = requests.post(url, headers=headers, data=json_payload, files=files)
    if response.status_code != 200:
        raise Exception(f"Failed to upload {local_file_path} to {dbfs_file_path}: {response.text}")
    print(f"Successfully uploaded {local_file_path} to {dbfs_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload files to Databricks DBFS")
    parser.add_argument("--databricks-instance", required=True, help="Databricks instance name (e.g., adb-xxxxxxxxxxxx.1.azuredatabricks.net)")
    parser.add_argument("--databricks-token", required=True, help="Databricks access token")
    parser.add_argument("--source-dir", required=True, help="Directory containing files to upload")
    parser.add_argument("--target-dir", required=True, help="DBFS target directory")

    args = parser.parse_args()

    for root, _, files in os.walk(args.source_dir):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, args.source_dir)
            dbfs_file_path = os.path.join(args.target_dir, relative_path)
            upload_file_to_dbfs(args.databricks_instance, args.databricks_token, local_file_path, dbfs_file_path)
