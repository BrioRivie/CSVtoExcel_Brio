import pandas as pd
import os
import textwrap
import io
import zipfile
import logging
from io import BytesIO

def process_csvs_to_excel(csv_files_dict, excel_filename):
    """
    Process multiple CSV files and convert them into a single Excel workbook
    with multiple sheets.
    
    Args:
        csv_files_dict (dict): Dictionary of {filename: blob_content} pairs
        excel_filename (str): The name for the Excel file (without extension)
    
    Returns:
        bytes: The Excel workbook as bytes
    """
    logging.info(f"Converting multiple CSVs to a single Excel file: {excel_filename}.xlsx")
    logging.info(f"Number of CSV files to process: {len(csv_files_dict)}")
    
    # Create a BytesIO object for the Excel output
    excel_output = BytesIO()
    
    # Create Excel writer
    writer = pd.ExcelWriter(excel_output, engine='xlsxwriter')
    
    try:
        # Process each CSV file as a separate sheet
        sheet_count = 0
        for filename, blob_content in csv_files_dict.items():
            try:
                # Extract just the filename without extension for sheet name
                file_basename = os.path.basename(filename)
                sheet_name = os.path.splitext(file_basename)[0]
                
                # For formats like "csvfiles/File.csv", get only "File"
                if "/" in sheet_name:
                    sheet_name = sheet_name.split("/")[-1]
                
                # Read the CSV content
                df = pd.read_csv(BytesIO(blob_content))
                
                # Add the dataframe to the Excel file as a sheet
                add_sheet_to_excel(writer, df, sheet_name)
                sheet_count += 1
                
                # Log progress for every 10 sheets
                if sheet_count % 10 == 0:
                    logging.info(f"Processed {sheet_count} of {len(csv_files_dict)} sheets")
                    
            except Exception as e:
                logging.error(f"Error processing CSV file {filename}: {str(e)}")
                # Continue with other files even if one fails
        
        # Save the Excel file (use close instead of save in newer pandas versions)
        writer.close()
        excel_output.seek(0)
        logging.info(f"Successfully created Excel workbook with {sheet_count} sheets")
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
