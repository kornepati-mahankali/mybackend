import os
import pandas as pd
import fnmatch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "ireps")
statename = "ireps_merged"
print(OUTPUT_DIR)

file_prefix = "tenders_page"
# Collect all filenames matching the pattern in the OUTPUT_DIR
filenames = [os.path.join(OUTPUT_DIR, filename) 
             for filename in os.listdir(OUTPUT_DIR) 
             if fnmatch.fnmatch(filename, f"{file_prefix}*.xlsx")]

dataframes = []
for file_path in filenames:
    try:
        # Attempt to read the file
        df = pd.read_excel(file_path, engine='openpyxl')
        dataframes.append(df)
    except Exception as e:
        # Print out the error and the problematic file
        print(f"Error reading {file_path}: {e}")

if dataframes:
    # Merge all valid dataframes
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Save the merged dataframe to a new Excel file
    output_excel_file = os.path.join(OUTPUT_DIR, f"{statename}.xlsx")
    merged_df.to_excel(output_excel_file, index=False)
    print("Merged Excel file saved at:", output_excel_file)
else:
    print("No valid Excel files were found to merge.")
