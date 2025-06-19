# CSV to Excel Azure Function

This Azure Function App monitors a blob storage container for new CSV files and automatically converts them to Excel format.

## How It Works

When new CSV files are uploaded to the blob container, this function:

1. Detects the newly uploaded CSV file and converts it to Excel format
2. Checks all existing CSV files to ensure each has a corresponding Excel file
3. Creates Excel files for any CSV files that don't already have one

## Architecture

- **Trigger**: Blob trigger watching the path `testrowinfotool/csvfiles/{name}`
- **Input**: CSV files uploaded to the blob container
- **Processing**: Converts CSV data to Excel workbooks with appropriate sheet naming
- **Output**: Excel files stored in the `testrowinfotool/excelfiles/` directory

## Technical Details

### Function Components

- **CSVToExcelFunction/__init__.py**: Contains the main function entry point with blob trigger
- **CSVToExcelFunction/csv_excel_converter.py**: Utility module that handles the CSV to Excel conversion logic
- **CSVToExcelFunction/function.json**: Function configuration defining the blob trigger

### Processing Logic

1. When a new CSV file is uploaded to `testrowinfotool/csvfiles/`:
   - The function is triggered and processes that specific file
   - It extracts the filename without extension to use for the Excel file
   - It reads the CSV content and converts it to Excel format
   - It saves the Excel file to `testrowinfotool/excelfiles/`

2. After processing the triggering file, the function:
   - Lists all CSV files in the `csvfiles` directory
   - Lists all Excel files in the `excelfiles` directory
   - Identifies any CSV files that don't have corresponding Excel files
   - Processes those CSV files to create missing Excel files

3. Excel processing includes:
   - Handling sheet name length limitations (Excel's 31 character limit)
   - Preserving data integrity during conversion
   - Proper error handling and logging

## Configuration

### Local Settings

The function requires an Azure Storage connection string in `local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<your-storage-connection-string>",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

## Development

### Prerequisites

- Python 3.8 or later
- Azure Functions Core Tools
- Visual Studio Code with Azure Functions extension

### Running Locally

1. Clone this repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/MacOS: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the function locally: `func start`

### Testing

To test the function locally:
1. Set up Azurite for local blob storage emulation
2. Upload CSV files to the local blob storage container
3. Verify Excel files are created in the output directory

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
