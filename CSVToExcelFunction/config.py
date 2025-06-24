import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
import logging

class Config:
    """Configuration settings for the CSV to Excel converter function"""
    
    def __init__(self):
        # Set default values that can be overridden by environment variables
        self._storage_connection_string = None
        self._container_name = os.environ.get("BLOB_CONTAINER_NAME", "testrowinfotool")
        self._csv_directory = os.environ.get("CSV_DIRECTORY", "csvfiles")
        self._excel_directory = os.environ.get("EXCEL_DIRECTORY", "excelfiles")
        self._key_vault_url = os.environ.get("KEY_VAULT_URL", None)
        self._storage_connection_secret_name = os.environ.get("STORAGE_SECRET_NAME", "AzureWebJobsStorage")
        
        # Flag to determine if running in Azure or locally
        self._running_in_azure = os.environ.get("AZURE_FUNCTIONS_ENVIRONMENT") is not None
    
    def get_storage_connection_string(self):
        """
        Get storage connection string from environment or Key Vault
        """
        if self._storage_connection_string:
            return self._storage_connection_string
            
        # First try to get from environment variables (local development or app settings)
        conn_string = os.environ.get("AzureWebJobsStorage")
        
        # If running in Azure and Key Vault URL is provided, try to get from Key Vault
        if self._running_in_azure and self._key_vault_url and not conn_string.startswith("DefaultEndpoints"):
            try:
                # Use managed identity in Azure or DefaultAzureCredential for local dev
                credential = ManagedIdentityCredential() if self._running_in_azure else DefaultAzureCredential()
                client = SecretClient(vault_url=self._key_vault_url, credential=credential)
                conn_string = client.get_secret(self._storage_connection_secret_name).value
                logging.info("Retrieved storage connection string from Key Vault")
            except Exception as e:
                logging.error(f"Error retrieving connection string from Key Vault: {str(e)}")
                # Fall back to environment variable
                pass
        
        self._storage_connection_string = conn_string
        return conn_string
    
    @property
    def container_name(self):
        return self._container_name
        
    @property
    def csv_directory(self):
        return self._csv_directory
        
    @property
    def excel_directory(self):
        return self._excel_directory
        
    @property
    def csv_path_prefix(self):
        return f"{self._csv_directory}/"
        
    @property
    def excel_path_prefix(self):
        return f"{self._excel_directory}/"