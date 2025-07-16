import os
import pandas as pd
import fnmatch

# Setup base and output directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "OUTPUT")

# User inputs
statename = input("Enter your State Name: ").strip()
bid_user = input("Enter the Bid User Name: ").strip()
print("Reading files from:", OUTPUT_DIR)

# File prefix and matching
file_prefix = "open-tenders_"
filenames = [
    os.path.join(OUTPUT_DIR, filename)
    for filename in os.listdir(OUTPUT_DIR)
    if fnmatch.fnmatch(filename, f"{file_prefix}*.xlsx")
]

dataframes = []

# Header row to be removed if present in data
header_to_remove = [
    "Bid User", "Tender ID", "Name of Work", "Tender Category", "Department",
    "Quantity", "EMD", "Exemption", "ECV", "State Name", "Location",
    "Apply Mode", "Website", "Document Link", "Attachments", "Closing Date"
]

# Process each file
for file_path in filenames:
    try:
        df = pd.read_excel(file_path, engine='openpyxl')

        # Remove header row if accidentally repeated inside data
        df = df[~(df.apply(lambda row: row.tolist() == header_to_remove, axis=1))]

        # Drop 'Pincode' column if exists
        if 'Pincode' in df.columns:
            df = df.drop(columns=['Pincode'])

        # Copy 'Website' value to 'Document Link' and 'Attachments'
        if 'Website' in df.columns:
            if 'Document Link' in df.columns:
                df['Document Link'] = df['Website']
            if 'Attachments' in df.columns:
                df['Attachments'] = df['Website']

        # Move 'Attachments' column before 'Closing Date' if both exist
        if 'Attachments' in df.columns and 'Closing Date' in df.columns:
            col_order = df.columns.tolist()
            col_order.remove('Attachments')
            closing_index = col_order.index('Closing Date')
            col_order.insert(closing_index, 'Attachments')
            df = df[col_order]

        # Fill Bid User and State Name
        if 'Bid User' in df.columns:
            df['Bid User'] = bid_user
        if 'State Name' in df.columns:
            df['State Name'] = statename

        dataframes.append(df)

    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

# Merge and save output
if dataframes:
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Format 'Closing Date' column if it exists
    if 'Closing Date' in merged_df.columns:
        merged_df['Closing Date'] = pd.to_datetime(
            merged_df['Closing Date'], errors='coerce'
        ).dt.strftime('%d-%m-%Y %H:%M:%S')

    # Save final Excel file
    output_file = os.path.join(OUTPUT_DIR, f"{statename}.xlsx")
    merged_df.to_excel(output_file, index=False)
    print("✅ Merged Excel file saved at:", output_file)
else:
    print("⚠️ No valid Excel files were found to merge.")
