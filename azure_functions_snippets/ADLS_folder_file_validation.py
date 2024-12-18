import logging
import os
import json
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from jsonschema import validate, ValidationError
from azure.functions import HttpRequest, HttpResponse

# JSON schema for validation
SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "created_at": {"type": "string", "format": "date-time"}
    },
    "required": ["id", "name", "email", "created_at"]
}

# ADLS configuration
ADLS_STORAGE_ACCOUNT_NAME = os.getenv("ADLS_STORAGE_ACCOUNT_NAME")
ADLS_CONTAINER_NAME = os.getenv("ADLS_CONTAINER_NAME")
INPUT_FOLDER = "input/"
OUTPUT_FOLDER = "output/"
ERROR_FOLDER = "error/"

# Initialize ADLS service client
def get_adls_service_client():
    credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(
        account_url=f"https://{ADLS_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
        credential=credential
    )
    return service_client

# Validate JSON file content
def validate_json(content):
    try:
        validate(instance=content, schema=SCHEMA)
        return True, None
    except ValidationError as e:
        return False, str(e)

# Move a file from one folder to another in ADLS
def move_file(service_client, file_system_name, source_path, destination_path):
    file_system_client = service_client.get_file_system_client(file_system=file_system_name)
    source_file = file_system_client.get_file_client(source_path)
    destination_file = file_system_client.get_file_client(destination_path)

    # Copy the file
    destination_file.create_file()
    destination_file.append_data(source_file.download_file().readall(), 0)
    destination_file.flush_data(len(source_file.download_file().readall()))

    # Delete the source file
    source_file.delete_file()

def main(req: HttpRequest) -> HttpResponse:
    logging.info("HTTP-triggered function to validate and move JSON files started.")

    service_client = get_adls_service_client()
    file_system_client = service_client.get_file_system_client(ADLS_CONTAINER_NAME)
    input_folder_client = file_system_client.get_directory_client(INPUT_FOLDER)

    # List all files in the input folder
    try:
        paths = input_folder_client.get_paths()
    except Exception as e:
        logging.error(f"Error accessing input folder: {e}")
        return HttpResponse("Error accessing input folder.", status_code=500)

    # Iterate through files
    for path in paths:
        file_name = path.name.split("/")[-1]
        file_path = path.name

        try:
            file_client = file_system_client.get_file_client(file_path)
            file_data = file_client.download_file().readall()
            json_content = json.loads(file_data)
        except Exception as e:
            logging.error(f"Failed to read or parse file {file_name}: {e}")
            continue

        # Validate the file content
        is_valid, error_message = validate_json(json_content)

        # Define new file paths
        today_date = datetime.now().strftime("%Y-%m-%d")
        if is_valid:
            destination_path = f"{OUTPUT_FOLDER}{today_date}/{file_name}"
        else:
            destination_path = f"{ERROR_FOLDER}{today_date}/{file_name}"

        # Move the file
        try:
            move_file(service_client, ADLS_CONTAINER_NAME, file_path, destination_path)
            logging.info(f"File {file_name} moved to {'output' if is_valid else 'error'} folder.")
        except Exception as e:
            logging.error(f"Failed to move file {file_name}: {e}")

    return HttpResponse("File processing completed.", status_code=200)
