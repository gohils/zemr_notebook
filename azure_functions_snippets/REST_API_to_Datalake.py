import datetime
import os
import json
import requests
from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient

# Service Principal credentials and Azure Data Lake settings
TENANT_ID = os.environ["TENANT_ID"]          # Azure AD Tenant ID
CLIENT_ID = os.environ["CLIENT_ID"]          # Service Principal Client ID
CLIENT_SECRET = os.environ["CLIENT_SECRET"]  # Service Principal Client Secret
STORAGE_ACCOUNT_NAME = os.environ["STORAGE_ACCOUNT_NAME"]  # ADLS Storage Account Name
CONTAINER_NAME = os.environ["CONTAINER_NAME"]             # ADLS File System (Container) Name

# List of URLs to pull data from
URLS = [
    "https://jsonplaceholder.typicode.com/posts",
    "https://jsonplaceholder.typicode.com/comments"
]

def authenticate_datalake():
    """Authenticate to Azure Data Lake using Service Principal."""
    credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    datalake_service_client = DataLakeServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
        credential=credential
    )
    return datalake_service_client

def upload_file_to_datalake(file_system_client, local_file_path, remote_file_path):
    """Upload a file to Azure Data Lake."""
    try:
        # Create or get the directory
        remote_directory = os.path.dirname(remote_file_path)
        directory_client = file_system_client.get_directory_client(remote_directory)
        directory_client.create_directory()

        # Upload the file
        file_client = file_system_client.get_file_client(remote_file_path)
        with open(local_file_path, "rb") as file_data:
            file_client.upload_data(file_data, overwrite=True)
        print(f"Uploaded: {remote_file_path}")
    except Exception as e:
        print(f"Error uploading {remote_file_path}: {str(e)}")

def main(mytimer):
    """Azure Function Timer Trigger."""
    try:
        # Authenticate to Data Lake
        service_client = authenticate_datalake()
        file_system_client = service_client.get_file_system_client(file_system=CONTAINER_NAME)

        # Create date-based folder name
        current_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        remote_base_folder = f"api_data/{current_date}"
        local_base_folder = "/tmp/api_data"  # Local temporary folder

        # Ensure local base folder exists
        os.makedirs(local_base_folder, exist_ok=True)

        # Process each URL
        for index, url in enumerate(URLS):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # Save API response to a local JSON file
                    file_name = f"api_response_{index+1}.json"
                    local_file_path = os.path.join(local_base_folder, file_name)
                    with open(local_file_path, "w") as f:
                        json.dump(response.json(), f, indent=4)

                    # Define remote file path
                    remote_file_path = f"{remote_base_folder}/{file_name}"

                    # Upload the file to Data Lake
                    upload_file_to_datalake(file_system_client, local_file_path, remote_file_path)
                else:
                    print(f"Failed to fetch data from {url}. Status Code: {response.status_code}")
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")
    except Exception as e:
        print(f"Function execution failed: {str(e)}")
