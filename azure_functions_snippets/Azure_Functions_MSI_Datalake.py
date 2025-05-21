''' 
How to Use MSI in Azure Function to Write to ADLS Gen2
1. Prerequisites
Your Azure Function App has a System-Assigned Managed Identity enabled.

That identity has been granted Storage Blob Data Contributor or Storage Blob Data Owner role on the ADLS Gen2 account at the appropriate scope (container or root level).

2. Install Required Library
pip install azure-identity azure-storage-file-datalake

4. Assign Role to Managed Identity
Go to Azure Portal:

Navigate to your ADLS Gen2 storage account.

Go to Access Control (IAM).

Assign Storage Blob Data Contributor role to your Azure Function's system-assigned managed identity.

'''

# Python Function Using Managed Identity
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import ResourceExistsError

def upload_to_adls_with_msi(account_name, file_system_name, directory_name, file_name, content):
    """
    Uploads text content to Azure Data Lake Storage Gen2 using Managed Identity (MSI).

    Parameters:
        account_name (str): Storage account name.
        file_system_name (str): Filesystem (container) name.
        directory_name (str): Directory in the container.
        file_name (str): File name to upload.
        content (str): Content to be written to the file.
    """
    try:
        # Use managed identity for authentication
        credential = DefaultAzureCredential()

        # Create DataLakeServiceClient with MSI
        service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=credential
        )

        # Get the file system client (container)
        file_system_client = service_client.get_file_system_client(file_system_name)

        # Create or get the directory
        try:
            directory_client = file_system_client.create_directory(directory_name)
        except ResourceExistsError:
            directory_client = file_system_client.get_directory_client(directory_name)

        # Create the file and upload content
        file_client = directory_client.create_file(file_name)
        file_client.append_data(data=content, offset=0, length=len(content))
        file_client.flush_data(len(content))

        print(f"Uploaded '{file_name}' to ADLS Gen2 via MSI.")

    except Exception as e:
        print(f"MSI ADLS upload error: {e}")

import json

# Convert dictionary to JSON string
json_content = json.dumps(content_of_file, indent=2)

# Save raw JSON string directly to file
with open(file_name, 'w', encoding='utf-8') as json_file:
    json_file.write(json_content)

# Save JSON string to ADLS
upload_to_adls_with_msi(
    account_name="your-storage-account",
    file_system_name="your-filesystem",
    directory_name="your-directory",
    file_name="yourfile.json",
    content=json_content
)
