import pandas as pd
import json

excel_file = "Spanish.xlsx"
json_file = "Tleft.json"

# Load JSON keys
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Load Excel keys (all sheets)
sheets = pd.read_excel(excel_file, sheet_name=None)
excel_keys = set()
for df in sheets.values():
    if not df.empty and df.shape[1] >= 1:
        # Add stripped and non-stripped versions to check
        keys = df.iloc[:, 0].astype(str).tolist()
        for k in keys:
            excel_keys.add(k)
            excel_keys.add(k.strip())

# Test specific keys that failed
test_keys = [
    "Categories"
]

print(f"Total Excel keys loaded: {len(excel_keys)}")

for key in test_keys:
    print(f"\nTesting key: '{key}'")
    found_any = False
    for ek in excel_keys:
        if key.lower() in ek.lower():
            print(f"  -> Found partial match: '{ek}'")
            found_any = True
    
    if not found_any:
        print("  -> No match found.")
