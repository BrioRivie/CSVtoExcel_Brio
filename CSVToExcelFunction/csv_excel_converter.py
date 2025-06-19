import pandas as pd
import os
import textwrap
import io
import zipfile
import logging
from io import BytesIO

def process_csvs_to_excel(blob_content, client_name):
    """
    Process a CSV file from a blob and convert it to an Excel workbook.
    
    Args:
        blob_content (bytes): The content of the blob containing a CSV file
        client_name (str): The name of the CSV file (without extension)
    
    Returns:
        bytes: The Excel workbook as bytes
    """
    logging.info(f"Converting CSV to Excel for: {client_name}")
    
    # Create a BytesIO object for the Excel output
    excel_output = BytesIO()
    
    # Create Excel writer
    writer = pd.ExcelWriter(excel_output, engine='xlsxwriter')
    
    try:
        # Process as a single CSV file
        try:
            # Read the CSV content
            df = pd.read_csv(BytesIO(blob_content))
            
            # Add the dataframe to the Excel file
            add_sheet_to_excel(writer, df, client_name)
        except Exception as e:
            logging.error(f"Error reading CSV content: {str(e)}")
            raise
                  # Save the Excel file (use close instead of save in newer pandas versions)
        writer.close()
        excel_output.seek(0)
        return excel_output.getvalue()
    except Exception as e:
        logging.error(f"Error in process_csvs_to_excel: {str(e)}")
        # Make sure we close the writer even if an error occurs
        try:
            writer.close()
        except:
            pass
        raise

def add_sheet_to_excel(writer, df, sheet_name):
    """
    Add a dataframe as a sheet to an Excel writer, handling sheet name limitations.
    
    Args:
        writer: Excel writer
        df: DataFrame to add
        sheet_name: Name for the sheet
    """
    logging.info(f"Adding sheet: {sheet_name}")
    
    try:
        # Check if sheet name is longer than Excel's limit (31 chars)
        if len(sheet_name) <= 31:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            logging.info(f"Sheet name too long: {sheet_name}")
            # Shorten the name
            shortened_name = textwrap.shorten(sheet_name, width=30, placeholder='')
            logging.info(f"Shortened to: {shortened_name}")
            df.to_excel(writer, sheet_name=shortened_name, index=False)
    except Exception as e:
        logging.error(f"Error adding sheet '{sheet_name}': {str(e)}")
        raise
