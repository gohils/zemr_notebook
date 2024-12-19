from azure.identity import ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient

def list_data_retention_policy(subscription_id, resource_group_name, storage_account_name, client_id, client_secret, tenant_id):
    """
    List the data retention policy for an Azure Data Lake Storage account using service principal authentication.

    Args:
        subscription_id (str): Your Azure subscription ID.
        resource_group_name (str): The resource group of the storage account.
        storage_account_name (str): The name of the storage account.
        client_id (str): The client ID of the service principal.
        client_secret (str): The client secret of the service principal.
        tenant_id (str): The tenant ID for the service principal.
    """
    try:
        # Authenticate using the service principal
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        storage_client = StorageManagementClient(credential, subscription_id)
        
        # Get the storage account properties
        storage_account = storage_client.storage_accounts.get_properties(resource_group_name, storage_account_name)
        
        # Check if the account supports hierarchical namespace (ADLS Gen2)
        if storage_account.is_hns_enabled:
            print(f"Storage Account '{storage_account_name}' supports Data Lake (Hierarchical Namespace).")
            print("Checking for data retention policies...")
            
            # Fetch and display data retention policy details
            blob_services = storage_client.blob_services.get(resource_group_name, storage_account_name, "default")
            if blob_services.delete_retention_policy:
                policy = blob_services.delete_retention_policy
                if policy.enabled:
                    print("Delete Retention Policy is enabled.")
                    print(f" - Retention Days: {policy.days}")
                else:
                    print("Delete Retention Policy is disabled.")
            else:
                print("No delete retention policy found.")
        else:
            print(f"Storage Account '{storage_account_name}' does not support Data Lake features (HNS not enabled).")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace these variables with your Azure service principal details and subscription info
subscription_id = "your-subscription-id"
resource_group_name = "your-resource-group-name"
storage_account_name = "your-storage-account-name"

# Service principal credentials
client_id = "your-client-id"
client_secret = "your-client-secret"
tenant_id = "your-tenant-id"

# Call the function
list_data_retention_policy(subscription_id, resource_group_name, storage_account_name, client_id, client_secret, tenant_id)
