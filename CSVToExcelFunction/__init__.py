import logging
import azure.functions as func
from io import BytesIO
import os
import re
from azure.storage.blob import BlobServiceClient
from .csv_excel_converter import process_csvs_to_excel
from .config import Config

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processing blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    # Initialize configuration
    config = Config()
    
    # Process the currently triggered CSV file
    process_current_csv(myblob, config)
    
    # Then check all CSVs to make sure they have corresponding Excel files
    process_all_csvs(config)

def process_current_csv(myblob: func.InputStream, config: Config):
    """Process the currently triggered CSV file"""
    # Extract file name from blob path
    # Expected format: containername/csvfiles/filename.csv
    blob_path_parts = myblob.name.split('/')
    if len(blob_path_parts) >= 3:
        file_name = blob_path_parts[-1]  # Get just the filename
        # Use regex to properly extract filename without extension
        match = re.search(r'(.+)\.csv$', file_name, re.IGNORECASE)
        if match:
            file_name_without_ext = match.group(1)
        else:
            file_name_without_ext = file_name.rsplit('.', 1)[0]  # Remove extension
    else:
        file_name_without_ext = "unknown"  # Default fallback
        logging.warning(f"Unexpected blob path format: {myblob.name}")
    
    logging.info(f"Processing triggered CSV file: {file_name_without_ext}")
    
    try:
        # Read the blob content
        blob_content = myblob.read()
        
        # Process CSV to Excel
        excel_bytes = process_csvs_to_excel(blob_content, file_name_without_ext)
        
        # Write the Excel file directly to Azure Blob Storage
        connection_string = config.get_storage_connection_string()
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = config.container_name
        
        # Create the Excel file in the excelfiles directory with the correct name
        excel_blob_name = f"{config.excel_directory}/{file_name_without_ext}.xlsx"
        excel_blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=excel_blob_name
        )
        
        # Upload the Excel content
        excel_blob_client.upload_blob(excel_bytes, overwrite=True)
        
        logging.info(f"Successfully created Excel file: {excel_blob_name}")
    except Exception as e:
        logging.error(f"Error processing triggered CSV data for {file_name_without_ext}: {str(e)}")
        # Re-raise the exception to ensure Azure Functions knows this execution failed
        raise

def process_all_csvs(config: Config):
    """Check all CSV files and ensure they have corresponding Excel files"""
    try:
        logging.info("Starting to check all CSV files for corresponding Excel files")
        
        # Get connection string from config
        connection_string = config.get_storage_connection_string()
        
        # Create BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get container name from config
        container_name = config.container_name
        container_client = blob_service_client.get_container_client(container_name)
        
        # List all blobs in csvfiles virtual directory
        csv_blobs = []
        csv_prefix = config.csv_path_prefix
        csv_blob_list = container_client.list_blobs(name_starts_with=csv_prefix)
        
        for blob in csv_blob_list:
            if blob.name.lower().endswith('.csv'):
                csv_blobs.append(blob.name)
        
        logging.info(f"Found {len(csv_blobs)} total CSV files in the {config.csv_directory} directory")
        
        # List all blobs in excelfiles virtual directory
        excel_blobs = []
        excel_prefix = config.excel_path_prefix
        excel_blob_list = container_client.list_blobs(name_starts_with=excel_prefix)
        
        for blob in excel_blob_list:
            if blob.name.lower().endswith('.xlsx'):
                excel_blobs.append(blob.name)
        
        logging.info(f"Found {len(excel_blobs)} total Excel files in the {config.excel_directory} directory")
        
        # Create a map of Excel filenames without extension for easy lookup
        excel_files_map = {}
        for excel_blob in excel_blobs:
            # Extract just the filename without path or extension
            match = re.search(f"{config.excel_directory}/(.+)\\.xlsx$", excel_blob)
            if match:
                filename = match.group(1)
                excel_files_map[filename] = excel_blob
        
        # Process each CSV file that doesn't have a corresponding Excel file
        processed_count = 0
        for csv_blob in csv_blobs:
            # Extract just the filename without path or extension
            match = re.search(f"{config.csv_directory}/(.+)\\.csv$", csv_blob)
            if match:
                csv_filename = match.group(1)
                
                # Check if there's a corresponding Excel file
                if csv_filename not in excel_files_map:
                    logging.info(f"Found CSV without corresponding Excel file: {csv_blob}")
                    
                    # Process this CSV file
                    try:
                        # Download the blob content
                        blob_client = blob_service_client.get_blob_client(
                            container=container_name, 
                            blob=csv_blob
                        )
                        
                        # Download the blob content
                        blob_content = blob_client.download_blob().readall()
                        
                        # Process CSV to Excel
                        excel_bytes = process_csvs_to_excel(blob_content, csv_filename)
                        
                        # Create the Excel file in the excelfiles directory
                        excel_blob_name = f"{config.excel_directory}/{csv_filename}.xlsx"
                        excel_blob_client = blob_service_client.get_blob_client(
                            container=container_name, 
                            blob=excel_blob_name
                        )
                        
                        # Upload the Excel content
                        excel_blob_client.upload_blob(excel_bytes, overwrite=True)
                        processed_count += 1
                        logging.info(f"Successfully processed CSV: {csv_blob} -> {excel_blob_name}")
                    except Exception as e:
                        logging.error(f"Error processing CSV {csv_blob}: {str(e)}")
                        # Continue processing other files even if one fails
        
        logging.info(f"Completed check of all CSV files. Processed {processed_count} previously unprocessed files.")
    except Exception as e:
        logging.error(f"Error in process_all_csvs: {str(e)}")
        # Don't re-raise so the main function can complete
