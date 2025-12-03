import pandas as pd

excel_file = "Spanish.xlsx"
sheet_name = "Cloud Services"

try:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    # Print first 5 rows of English AND German (2nd column)
    print(f"Sheet: {sheet_name}")
    print(f"Columns: {df.columns.tolist()}")
    
    print("\nFirst 5 rows:")
    for i in range(5):
        eng = df.iloc[i, 0]
        ger = df.iloc[i, 1]
        print(f"Row {i}:")
        print(f"  English: {eng}")
        print(f"  German:  {ger}")
        print("-" * 20)

except Exception as e:
    print(f"Error: {e}")
