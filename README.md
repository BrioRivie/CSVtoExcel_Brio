# CSV to Excel Azure Function

This Azure Function App monitors a blob storage container for new CSV files and automatically converts them to Excel format.

## How It Works

When new CSV files are uploaded to the blob container, this function:

1. Detects the newly uploaded CSV file and converts it to Excel format
2. Checks all existing CSV files to ensure each has a corresponding Excel file
3. Creates Excel files for any CSV files that don't already have one

## Architecture

- **Trigger**: Blob trigger watching the configured path `%BLOB_CONTAINER_NAME%/%CSV_DIRECTORY%/{name}`
- **Input**: CSV files uploaded to the blob container
- **Processing**: Converts CSV data to Excel workbooks with appropriate sheet naming
- **Output**: Excel files stored in the configured Excel directory

## Configuration

### Application Settings

The function can be configured with the following environment variables:

| Setting | Description | Default |
|---------|-------------|---------|
| AzureWebJobsStorage | Storage account connection string (or Key Vault reference) | - |
| BLOB_CONTAINER_NAME | Name of the blob container | testrowinfotool |
| CSV_DIRECTORY | Directory within container for CSV files | csvfiles |
| EXCEL_DIRECTORY | Directory within container for Excel files | excelfiles |
| KEY_VAULT_URL | Azure Key Vault URL for secrets (optional) | - |
| STORAGE_SECRET_NAME | Name of the secret in Key Vault for storage connection | AzureWebJobsStorage |

### Azure Key Vault Integration

For production deployments, it's recommended to use Azure Key Vault to store sensitive information like connection strings:

1. Create a Key Vault and add the storage connection string as a secret
2. Assign a managed identity to your Function App
3. Grant the Function App identity permission to access secrets in the Key Vault
4. Configure your Function App with the KEY_VAULT_URL setting
5. Replace the direct connection string with a Key Vault reference in application settings

### Local Settings

For local development, use `local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<your-storage-connection-string>",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "BLOB_CONTAINER_NAME": "testrowinfotool",
    "CSV_DIRECTORY": "csvfiles",
    "EXCEL_DIRECTORY": "excelfiles"
  }
}
```

## Development

### Prerequisites

- Python 3.8 or later
- Azure Functions Core Tools
- Visual Studio Code with Azure Functions extension
- Azure Storage Explorer
  
### Running Locally

1. Clone this repository
2. Create a virtual environment: `python -m venv .venv` (recommended to use virtual env, but I did not)
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/MacOS: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the function locally: `func start`

### Testing

To test the function locally:
1. Create a new storage accout (called testrowinfotool) (I already made this storage account under brio development subscription) and create a new blob container for the test data (for me this was testrowinfotool)
2. Copy the csvfiles directory from rowinfotool into your test blob container
3. copy and rename a csv file to use for simulation of adding a file in tests
4. run 'func start' in your terminal
5. Open the test blob container in azure storage and add a csv file to csvfiles directory
6. Check that excelfiles directory was created and has new content added to it as well as all csv files from before, all of these files should be .xlsx extensions


## Deployment

### Deploying to Azure

Deploy using VS Code:
1. Sign in to Azure in VS Code
2. Right-click on the project folder and select "Deploy to Function App..."
3. Follow the prompts to select or create a Function App in Azure

Alternatively, deploy using Azure Functions Core Tools:
```bash
func azure functionapp publish <your-function-app-name>
```

## Dependencies

- azure-functions
- azure-storage-blob
- pandas
- openpyxl
- xlsxwriter
