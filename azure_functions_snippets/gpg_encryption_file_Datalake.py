import os
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient, BlobClient
import gnupg

# Azure configurations
TENANT_ID = os.environ["TENANT_ID"]          # Azure AD Tenant ID
CLIENT_ID = os.environ["CLIENT_ID"]          # Service Principal Client ID
CLIENT_SECRET = os.environ["CLIENT_SECRET"]  # Service Principal Client Secret
KEY_VAULT_URL = os.environ["KEY_VAULT_URL"]  # Key Vault URL (e.g., https://<vault-name>.vault.azure.net/)
GPG_KEY_SECRET_NAME = os.environ["GPG_KEY_SECRET_NAME"]  # Name of the secret storing the GPG public key
STORAGE_ACCOUNT_URL = os.environ["STORAGE_ACCOUNT_URL"]  # Blob service URL (e.g., https://<account-name>.blob.core.windows.net/)
INPUT_CONTAINER = os.environ["INPUT_CONTAINER"]         # Input container name
OUTPUT_CONTAINER = os.environ["OUTPUT_CONTAINER"]       # Output container name

def authenticate_service_principal():
    """Authenticate with Azure services using a service principal."""
    return ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)

def fetch_gpg_key(secret_client):
    """Retrieve the GPG public key from Azure Key Vault."""
    secret = secret_client.get_secret(GPG_KEY_SECRET_NAME)
    return secret.value

def encrypt_file(gpg, gpg_key, input_file_path, output_file_path):
    """Encrypt a file using GPG."""
    with open(input_file_path, "rb") as input_file:
        status = gpg.encrypt_file(
            input_file,
            recipients=None,
            always_trust=True,
            output=output_file_path,
            armor=False,
            symmetric=True,
            passphrase=gpg_key
        )
        if not status.ok:
            raise Exception(f"Encryption failed: {status.status}")
    print(f"File encrypted successfully: {output_file_path}")

def download_blob(blob_client, download_path):
    """Download a blob to a local file."""
    with open(download_path, "wb") as file:
        blob_data = blob_client.download_blob()
        file.write(blob_data.readall())
    print(f"Downloaded blob to: {download_path}")

def upload_blob(blob_client, upload_path):
    """Upload a file to Azure Blob Storage."""
    with open(upload_path, "rb") as file:
        blob_client.upload_blob(file, overwrite=True)
    print(f"Uploaded file: {upload_path}")

def main(mytimer):
    """Azure Function Timer Trigger."""
    try:
        # Authenticate with Azure services
        credential = authenticate_service_principal()

        # Set up clients
        key_vault_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
        blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)

        # Fetch the GPG key from Key Vault
        gpg_key = fetch_gpg_key(key_vault_client)

        # Set up GPG
        gpg = gnupg.GPG()

        # List blobs in the input container
        input_container_client = blob_service_client.get_container_client(INPUT_CONTAINER)
        output_container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER)

        for blob in input_container_client.list_blobs():
            input_blob_client = input_container_client.get_blob_client(blob)
            output_blob_client = output_container_client.get_blob_client(blob.name + ".gpg")

            # Download the file
            input_file_path = f"/tmp/{blob.name}"
            download_blob(input_blob_client, input_file_path)

            # Encrypt the file
            output_file_path = input_file_path + ".gpg"
            encrypt_file(gpg, gpg_key, input_file_path, output_file_path)

            # Upload the encrypted file
            upload_blob(output_blob_client, output_file_path)

            # Clean up local files
            os.remove(input_file_path)
            os.remove(output_file_path)
    except Exception as e:
        print(f"Function execution failed: {str(e)}")
