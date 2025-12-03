import pandas as pd
import json
import os

excel_path = "Spanish.xlsx"
json_path = "Tleft.json"

print(f"--- Inspecting {excel_path} ---")
try:
    xl = pd.ExcelFile(excel_path)
    print(f"Sheet names: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        print(f"\nSheet: {sheet}")
        df = pd.read_excel(excel_path, sheet_name=sheet)
        print(f"Columns: {list(df.columns)}")
        print(f"Shape: {df.shape}")
        print("First 5 rows:")
        print(df.head())
        
        # Check for potential issues in the first column (English)
        if not df.empty:
            first_col = df.iloc[:, 0].astype(str)
            print("\nSample values from first column:")
            print(first_col.head().tolist())
            
            # Check for leading/trailing whitespace
            whitespace_count = first_col.str.match(r'^\s|\s$').sum()
            print(f"Rows with leading/trailing whitespace in first column: {whitespace_count}")
            
except Exception as e:
    print(f"Error reading Excel: {e}")

print(f"\n--- Inspecting {json_path} ---")
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    def get_strings(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                yield from get_strings(v)
        elif isinstance(obj, list):
            for item in obj:
                yield from get_strings(item)
        elif isinstance(obj, str):
            yield obj

    strings = list(get_strings(data))
    print(f"Total strings in JSON: {len(strings)}")
    print("First 10 strings:")
    print(strings[:10])
    
except Exception as e:
    print(f"Error reading JSON: {e}")
