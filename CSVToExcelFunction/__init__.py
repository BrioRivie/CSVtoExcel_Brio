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
    
    # Simplified approach: Always process all CSV files into a single Excel file
    excel_filename = "BrioCSVs"  # Fixed name for the Excel file
    logging.info(f"Processing all CSV files into a single Excel file: {excel_filename}.xlsx")
    
    # Process all CSVs in the csvfiles directory into one Excel workbook
    process_all_csvs(excel_filename, config)

def process_all_csvs(excel_filename, config):
    """Process all CSV files in the csvfiles directory into a single Excel workbook"""
    try:
        logging.info(f"Processing all CSV files into a single Excel file: {excel_filename}.xlsx")
        
        # Get connection string from config
        connection_string = config.get_storage_connection_string()
        
        # Create BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get container name from config
        container_name = config.container_name
        container_client = blob_service_client.get_container_client(container_name)
        
        # List all blobs in csvfiles virtual directory
        csv_blobs = {}
        csv_blob_list = container_client.list_blobs(name_starts_with=config.csv_path_prefix)
        
        csv_count = 0
        # Find all CSV files
        for blob in csv_blob_list:
            if blob.name.lower().endswith('.csv'):
                try:
                    # Log every 10th blob for progress tracking
                    if csv_count % 10 == 0:
                        logging.info(f"Processing CSV file #{csv_count}: {blob.name}")
                    
                    # Download the blob content
                    blob_client = blob_service_client.get_blob_client(
                        container=container_name, 
                        blob=blob.name
                    )
                    blob_content = blob_client.download_blob().readall()
                    csv_blobs[blob.name] = blob_content
                    csv_count += 1
                except Exception as blob_ex:
                    logging.error(f"Error downloading blob {blob.name}: {str(blob_ex)}")
                    # Continue with other blobs
        
        # If no CSV files found, log and return
        if not csv_blobs:
            logging.warning(f"No CSV files found in {config.csv_directory} directory")
            return
            
        logging.info(f"Found {len(csv_blobs)} total CSV files")
        
        # Process all CSV files into a single Excel workbook
        excel_bytes = process_csvs_to_excel(csv_blobs, excel_filename)
        
        # Create the Excel file in the excelfiles directory
        excel_blob_name = f"{config.excel_directory}/{excel_filename}.xlsx"
        excel_blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=excel_blob_name
        )
        
        # Upload the Excel content
        excel_blob_client.upload_blob(excel_bytes, overwrite=True)
        
        logging.info(f"Successfully created Excel file: {excel_blob_name} with {len(csv_blobs)} sheets")
        
    except Exception as e:
        logging.error(f"Error in process_all_csvs: {str(e)}")
        raise


