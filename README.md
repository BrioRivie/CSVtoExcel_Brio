# CSV to Excel Azure Function

This Azure Function App processes blobs containing multiple CSV files from the Azure Row Info Pipeline and converts them into Excel workbooks.

## Overview

The Azure Row Info Pipeline feeds CSVs into blob storage. For each client's blob, this function pools all CSV files into one Excel workbook with multiple tabs and places it in blob storage for user download.

The project contains:

**CSVToExcelFunction**: A blob-triggered function that processes a client blob containing multiple CSV files.
- Triggers when a new client blob is uploaded to the `client-data` container
- Processes all CSV files within that blob
- Creates a single Excel workbook with all CSVs as separate tabs
- Saves the Excel file to the `excel-output` container

## Container Structure

The function works with the following container structure:
- `client-data/{client-name}`: Contains multiple CSV files for a specific client
- `excel-output/{client-name}.xlsx`: Where the resulting Excel files are stored

## Configuration

### Local Settings

Update `local.settings.json` with the appropriate connection strings:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "<your-storage-connection-string>"
  }
}
```

## Blob Processing Logic

The function can handle client data in two formats:

1. A zip file containing multiple CSV files
2. A blob container with multiple CSV files

For each client, the function:
1. Reads all CSV files
2. Creates an Excel workbook with each CSV as a separate tab
3. Handles sheet name length constraints (Excel limit is 31 characters)
4. Saves the Excel workbook to blob storage

## Running Locally

1. Ensure you have Azure Functions Core Tools installed
2. Run `func start` to start the local function app

## Deployment

Deploy to Azure using VS Code Azure Functions extension:

1. Click on the Azure icon in VS Code
2. Navigate to "Functions"
3. Click "Deploy to Function App..."
4. Select your subscription and function app

## Dependencies

- azure-functions
- azure-storage-blob
- pandas
- openpyxl
- xlsxwriter
