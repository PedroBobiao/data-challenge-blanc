import pandas as pd
import os

# Define the input and output paths
EXCEL_FILE_PATH = 'data/Sample - Superstore.xlsx'
OUTPUT_DIR = 'data/'

def extract_sheets_to_csv(excel_path, sheets, output_dir):
    """
    Extracts specified sheets from an Excel file and saves them as CSVs,
    explicitly using UTF-8 encoding.
    """
    print(f"Starting extraction from: {excel_path}")
    
    # 1. Check if the Excel file exists
    if not os.path.exists(excel_path):
        print(f"🛑 Error: Excel file not found at '{excel_path}'.")
        print("Please ensure you have downloaded 'Sample - Superstore.xlsx' and placed it in the 'data/' folder.")
        return

    # 2. Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 3. Read the entire Excel file, specifying only the sheets we need
        xlsx = pd.ExcelFile(excel_path)
        
        for sheet_name in sheets:
            csv_filename = f'{sheet_name.lower().replace(" ", "_")}.csv'
            csv_path = os.path.join(output_dir, csv_filename)

            print(f"Reading sheet: '{sheet_name}'...")
            
            # Read the specific sheet into a DataFrame
            df = pd.read_excel(xlsx, sheet_name)
            
            # Save the DataFrame to a CSV file, explicitly setting the encoding to UTF-8
            df.to_csv(csv_path, index=False, encoding='utf-8')
            
            print(f"✅ Successfully saved '{sheet_name}' to '{csv_path}' using UTF-8 encoding.")

    except Exception as e:
        print(f"An error occurred during processing: {e}")

if __name__ == '__main__':
    # List of sheet names to extract
    sheets_to_extract = ['Orders', 'Returns']
    
    extract_sheets_to_csv(EXCEL_FILE_PATH, sheets_to_extract, OUTPUT_DIR)