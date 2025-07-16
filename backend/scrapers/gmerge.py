import os
import glob
import pandas as pd
import fnmatch
import argparse

parser = argparse.ArgumentParser(description="Merges Excel files from GeM scraper.")
parser.add_argument("--statename", type=str, required=True, help="Name of the state to merge files for.")
parser.add_argument("--run_id", type=str, required=True, help="Unique run identifier.")
args = parser.parse_args()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "Gem", args.run_id)
statename = args.statename
print(OUTPUT_DIR)
file_prefix="gem_output_of"
filenames = [os.path.join(OUTPUT_DIR, filename) 
             for filename in os.listdir(OUTPUT_DIR) 
             if fnmatch.fnmatch(filename, f"{file_prefix}*.xlsx")]
dataframes=[]
# filenames=glob.glob(OUTPUT_DIR + f"{file_prefix}.xlsx")
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