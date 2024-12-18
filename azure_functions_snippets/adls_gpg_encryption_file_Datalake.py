#pip install azure-storage-file-datalake azure-identity gnupg

import logging
import os
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
import gnupg
from datetime import datetime

# Azure Data Lake Storage Configuration
ADLS_STORAGE_ACCOUNT_NAME = os.getenv("ADLS_STORAGE_ACCOUNT_NAME")
ADLS_CONTAINER_NAME = os.getenv("ADLS_CONTAINER_NAME")
INPUT_FOLDER = "input/"
OUTPUT_FOLDER = "output/"
GPG_KEY_ID = os.getenv("GPG_KEY_ID")  # GPG key ID (fingerprint or email)

# GPG Configuration
GPG_HOME = "/tmp/.gnupg"  # Temporary directory for GPG operations

# Initialize Azure Data Lake Service Client
def get_adls_service_client():
    credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(
        account_url=f"https://{ADLS_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
        credential=credential
    )
    return service_client

# Encrypt a file using GPG
def encrypt_file(file_content, gpg, key_id):
    encrypted_data = gpg.encrypt(file_content, recipients=[key_id], always_trust=True)
    if not encrypted_data.ok:
        raise Exception(f"GPG encryption failed: {encrypted_data.status}")
    return str(encrypted_data)

# Main Azure Function
def main(req):
    logging.info("HTTP-triggered function to encrypt files started.")

    # Initialize ADLS client and GPG
    service_client = get_adls_service_client()
    gpg = gnupg.GPG(gnupghome=GPG_HOME)
    file_system_client = service_client.get_file_system_client(file_system=ADLS_CONTAINER_NAME)
    input_folder_client = file_system_client.get_directory_client(INPUT_FOLDER)

    # List all files in the input folder
    try:
        paths = input_folder_client.get_paths()
    except Exception as e:
        logging.error(f"Error accessing input folder: {e}")
        return func.HttpResponse("Error accessing input folder.", status_code=500)

    # Iterate over files in the input folder
    for path in paths:
        file_name = path.name.split("/")[-1]
        file_path = path.name

        try:
            # Read the file from ADLS
            file_client = file_system_client.get_file_client(file_path)
            file_data = file_client.download_file().readall()

            # Encrypt the file content
            logging.info(f"Encrypting file: {file_name}")
            encrypted_content = encrypt_file(file_data.decode(), gpg, GPG_KEY_ID)

            # Define the output path with the current date
            today_date = datetime.now().strftime("%Y-%m-%d")
            output_path = f"{OUTPUT_FOLDER}{today_date}/{file_name}.gpg"

            # Write the encrypted file to ADLS
            output_file_client = file_system_client.get_file_client(output_path)
            output_file_client.create_file()
            output_file_client.append_data(encrypted_content.encode(), 0)
            output_file_client.flush_data(len(encrypted_content))

            # Optionally delete the original file
            file_client.delete_file()
            logging.info(f"File {file_name} encrypted and moved to output folder.")

        except Exception as e:
            logging.error(f"Failed to process file {file_name}: {e}")

    return func.HttpResponse("File encryption completed.", status_code=200)
