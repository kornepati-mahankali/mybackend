# import pandas as pd
# import os
# from os import *

# # Specify the directory where the Excel files are stored
# BASE_DIR = path.dirname(path.abspath(__file__))
# OUTPUT_DIR = path.join(BASE_DIR, "kpp")
# GOODS = path.join(OUTPUT_DIR,"goods")
# WORK = path.join(OUTPUT_DIR,"works")
# SERVICES = path.join(OUTPUT_DIR,"services")

# section = input("Choose option (goods/works/services)(press enter to merge all):").strip().lower()
# # Create an empty list to hold DataFrames
# df_list = []
# if section  == "goods":
#     # Loop through all files in the directory
#     for filename in os.listdir(GOODS):
#         # Check if "services" is in the file name    
#         if section in filename and filename.endswith('.xlsx'):
#             print(f"merging {section}")
#             file_path = os.path.join(OUTPUT_DIR, filename)
#             # Read each Excel file into a DataFrame
#             df = pd.read_excel(file_path)
#             # Append the DataFrame to the list
#             df_list.append(df)
#         else:
#             df = pd.read_excel(filename.endswith('.xlsx'))
#                 # Append the DataFrame to the list
#             df_list.append(df)


# # Concatenate all DataFrames in the list into a single DataFrame
# merged_df = pd.concat(df_list, ignore_index=True)

# # Save the merged DataFrame to a new Excel file
# output_file = OUTPUT_DIR+'merged_services.xlsx'
# merged_df.to_excel(output_file, index=False)

# print(f"Merged file saved as {output_file}")



# """
# import os
# import pandas as pd

# OUTPUT_DIR = 'output'

# def merge_files_in_dir(dir_path, output_file_name):
#     files_to_merge = [f for f in os.listdir(dir_path) if f.endswith('.xlsx')]
#     merged_data = []
#     for file in files_to_merge:
#         file_path = os.path.join(dir_path, file)
#         df = pd.read_excel(file_path)
#         merged_data.append(df)
#     merged_df = pd.concat(merged_data, ignore_index=True)
#     output_file_path = os.path.join(dir_path, output_file_name)
#     merged_df.to_excel(output_file_path, index=False)
#     print(f"Merged file saved to {output_file_path}")

# def merge_all_files_in_output_dir():
#     for root, dirs, files in os.walk(OUTPUT_DIR):
#         if root == OUTPUT_DIR:
#             # Merge all files in the output dir
#             merge_files_in_dir(root, 'all_merged.xlsx')
#         else:
#             # Merge files in each subdirectory
#             dir_name = os.path.basename(root)
#             output_file_name = f"{dir_name}_merged.xlsx"
#             merge_files_in_dir(root, output_file_name)

# if __name__ == '__main__':
#     merge_all_files_in_output_dir()
# """

import os
import glob
import pandas as pd
import fnmatch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "kpp")
GOODS_DIR = os.path.join(OUTPUT_DIR, "goods")
WORK_DIR = os.path.join(OUTPUT_DIR, "works")
SERVICES_DIR = os.path.join(OUTPUT_DIR, "services")

def merge_files_in_dir(dir_path, output_file_name):
    dataframes = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_excel(file_path, engine='openpyxl')
                    dataframes.append(df)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    if dataframes:
        merged_df = pd.concat(dataframes, ignore_index=True)
        output_file_path = os.path.join(dir_path, output_file_name)
        merged_df.to_excel(output_file_path, index=False)
        print(f"Merged file saved to {output_file_path}")
    else:
        print("No valid Excel files were found to merge.")

def merge_all_merged_files():
    dataframes = []
    for file in os.listdir(OUTPUT_DIR):
        if file in ['goods_merged.xlsx', 'works_merged.xlsx', 'services_merged.xlsx']:
            file_path = os.path.join(OUTPUT_DIR, file)
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
                dataframes.append(df)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    if dataframes:
        merged_df = pd.concat(dataframes, ignore_index=True)
        output_file_path = os.path.join(OUTPUT_DIR, 'all_merged.xlsx')
        merged_df.to_excel(output_file_path, index=False)
        print(f"All merged file saved to {output_file_path}")
    else:
        print("No valid merged Excel files were found.")

def main():
    section = input("Choose option (goods/works/services) or press enter to merge all: ").strip().lower()
    if section == "goods":
        merge_files_in_dir(GOODS_DIR, "goods_merged.xlsx")
    elif section == "works":
        merge_files_in_dir(WORK_DIR, "works_merged.xlsx")
    elif section == "services":
        merge_files_in_dir(SERVICES_DIR, "services_merged.xlsx")
    else:
        merge_files_in_dir(GOODS_DIR, "goods_merged.xlsx")
        merge_files_in_dir(WORK_DIR, "works_merged.xlsx")
        merge_files_in_dir(SERVICES_DIR, "services_merged.xlsx")
        # Merge all merged files
        dataframes = []
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                if file.endswith('_merged.xlsx'):
                    file_path = os.path.join(root, file)
                    try:
                        df = pd.read_excel(file_path, engine='openpyxl')
                        dataframes.append(df)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        if dataframes:
            merged_df = pd.concat(dataframes, ignore_index=True)
            output_file_path = os.path.join(OUTPUT_DIR, 'all_merged.xlsx')
            merged_df.to_excel(output_file_path, index=False)
            print(f"All merged file saved to {output_file_path}")
        else:
            print("No valid merged Excel files were found.")
if __name__ == '__main__':
    main()