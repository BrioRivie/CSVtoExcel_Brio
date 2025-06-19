<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# CSV to Excel Azure Function

This project is an Azure Function App that converts multiple CSV files from blob storage into a single Excel workbook using Python.

## Background
This code processes blobs containing multiple CSV files from the Azure Row Info Pipeline. For each client's blob, it pools all CSV files into one Excel workbook with multiple tabs and places it in blob storage for user download.

## Key Components
- CSVToExcelFunction: A blob-triggered function that processes a group of CSV files from a client's blob into a single Excel workbook
- converter_utils.py: Helper module with the conversion logic based on the original Python script

## Important Files
- local.settings.json: Contains Azure Storage connection strings
- host.json: Azure Functions runtime configuration
- requirements.txt: Python package dependencies

## Processing Flow
1. Row info tool feeds CSVs into blob storage
2. Function detects the blob and processes all CSVs in it
3. Creates a single Excel workbook with all CSVs as separate tabs
4. Places the resulting Excel file in blob storage for download

## Coding Guidelines
- Follow Python PEP 8 style guide
- Use appropriate error handling for blob storage operations
- Ensure compatibility with Azure Functions runtime v4
- Maintain the same functionality as the original Python script
- Optimize for large CSV files when necessary

# Original files:

## csvToExcel.py:

from math import fabs
import os
import string
import pandas as pd
import glob
import textwrap



def csvToExcel(account):


    xls_name = str(account) #Takes in the object for file name and converts to a string to be used later. 

    path = './' # Establishes a variable for the file path. 

    all_files= glob.glob(os.path.join(path, "*.csv")) #Creates variable for all the files. 


    writer = pd.ExcelWriter(xls_name+'.xlsx', engine='xlsxwriter') #establishes the writer and creates the excel file. 


    print('These files have a character length greater than 33:')

    for f in all_files: 

        df = pd.read_csv(f) # Take in the files 
        if len(os.path.splitext(os.path.basename(f))[0]) <= 31: #Checks to see if tab name is over the limit. 
            df.to_excel(writer, sheet_name = os.path.splitext(os.path.basename(f))[0], index=False) # If all good it writes to a file.
            

        else:
            print(os.path.splitext(os.path.basename(f))[0]) # Prints out the tabs with chars over the limit. 
            print('---------------------------------------------')
            others = os.path.splitext(os.path.basename(f))[0] #Assigns a variable for the higher len tabs. 
            others = textwrap.shorten(others, width=30, placeholder='') # Shortens the tabs. 
            df.to_excel(writer, sheet_name = others) #Writes tabs to file. 
           
            print(others) #Print renamed files 
    
    print('These tabs are now named above:  \n \n') #Show user what tabs are named now. 
    print('Job Complete!') 

    writer.save()

()





                    
## original main.py:

import csvToExcel
import sys 
import logging






def main():


    csvToExcel.csvToExcel('Bailey8744')




main()




