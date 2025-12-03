import pandas as pd

excel_file = "Spanish.xlsx"
search_terms = [
    "Ready to get",
    "Generate actionable insights",
    "started?"
]

try:
    xl = pd.ExcelFile(excel_file)
    print(f"Searching in {len(xl.sheet_names)} sheets...")
    
    for sheet_name in xl.sheet_names:
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            if df.empty:
                continue
            
            # Convert first column to string
            first_col_values = df.iloc[:, 0].astype(str).tolist()
            
            for val in first_col_values:
                for term in search_terms:
                    if term in val:
                        print(f"Found match in '{sheet_name}':")
                        print(f"  Excel Value: '{val}'")
                        print(f"  Term: '{term}'")
                        print("-" * 20)
        except Exception as e:
            print(f"Error reading sheet '{sheet_name}': {e}")

except Exception as e:
    print(f"Error: {e}")
