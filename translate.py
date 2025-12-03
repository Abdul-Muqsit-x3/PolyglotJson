import json
import pandas as pd

import sys

# Force UTF-8 encoding for stdout to prevent crashes on Windows
sys.stdout.reconfigure(encoding='utf-8')

def load_translation_excel(path):
    try:
        # Read all sheets
        sheets = pd.read_excel(path, sheet_name=None)
    except (ValueError, FileNotFoundError):
        print("Error: File not found or invalid Excel file.")
        return {}
    
    all_dfs = []
    for sheet_name, df in sheets.items():
        if not df.empty and df.shape[1] >= 2:
            # Take first two columns, rename to standard names
            temp_df = df.iloc[:, :2].copy()
            temp_df.columns = ["English", "German"]
            all_dfs.append(temp_df)
    
    if not all_dfs:
        return {}

    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df = combined_df.dropna(subset=["English", "German"])
    
    # Create dictionary: English -> German
    return dict(zip(combined_df["English"].astype(str).str.strip(), combined_df["German"].astype(str).str.strip()))


import re

def transfer_tags(source, target):
    """
    Transfers HTML tags from source string to target string based on relative text position,
    snapping to the nearest word boundary to avoid breaking words.
    """
    # 1. Extract tags and their positions relative to the CLEAN text
    tags = []
    
    # We need to iterate through the source and find tags, while keeping track of the "clean" index
    tag_matches = list(re.finditer(r'<[^>]+>', source))
    
    if not tag_matches:
        return target
        
    clean_source = ""
    last_idx = 0
    
    # This list will store (clean_index, tag_content)
    # clean_index is the index in the clean string WHERE the tag should be inserted (before that char)
    tags_to_insert = []
    
    current_clean_len = 0
    
    for match in tag_matches:
        # Text before this tag
        text_segment = source[last_idx:match.start()]
        clean_source += text_segment
        current_clean_len += len(text_segment)
        
        # Record this tag at the current clean length
        tags_to_insert.append({
            'tag': match.group(0),
            'clean_pos': current_clean_len
        })
        
        last_idx = match.end()
        
    # Append remaining text
    clean_source += source[last_idx:]
    source_len = len(clean_source)
    
    if source_len == 0:
        # If source was only tags? Just append tags to target? 
        # Or if target is empty?
        # Edge case. Let's just return target + tags or tags + target.
        # For now, just return target to be safe, or append tags.
        return target + "".join([t['tag'] for t in tags_to_insert])

    # 2. Calculate ratios and find positions in target
    target_len = len(target)
    
    # We need to insert tags into target. 
    # We should sort tags by position to insert correctly (they are already sorted by occurrence).
    # But we need to adjust indices as we insert.
    
    target_insertions = [] # (target_index, tag_string)
    
    for tag_info in tags_to_insert:
        ratio = tag_info['clean_pos'] / source_len
        target_pos = int(round(ratio * target_len))
        
        # Clamp to bounds
        target_pos = min(target_pos, target_len)
        
        # --- SNAP TO NEAREST BOUNDARY LOGIC ---
        # If we are not at a boundary, find the nearest one.
        # Boundaries: Start (0), End (len), or Space (' ').
        
        # Check if already at a boundary (start, end, or space at/before pos)
        is_boundary = False
        if target_pos == 0 or target_pos == target_len:
            is_boundary = True
        elif target[target_pos] == ' ' or target[target_pos-1] == ' ':
            is_boundary = True
            
        if not is_boundary:
            # Search Left
            left_dist = 0
            left_bound = target_pos
            while left_bound > 0:
                if target[left_bound-1] == ' ':
                    break
                left_bound -= 1
                left_dist += 1
                
            # Search Right
            right_dist = 0
            right_bound = target_pos
            while right_bound < target_len:
                if target[right_bound] == ' ':
                    break
                right_bound += 1
                right_dist += 1
            
            # Choose closer
            if left_dist <= right_dist:
                target_pos = left_bound
            else:
                target_pos = right_bound
        
        target_insertions.append((target_pos, tag_info['tag']))
        
    # Sort by position (stable sort to keep order of adjacent tags)
    target_insertions.sort(key=lambda x: x[0])
    
    # Construct result
    result = ""
    current_idx = 0
    
    for pos, tag in target_insertions:
        # Append text from last position to current tag position
        result += target[current_idx:pos]
        # Append tag
        result += tag
        current_idx = pos
        
    # Append remaining target text
    result += target[current_idx:]
    
    return result

def replace_values_with_logs(obj, translations, report):
    """
    Recursively replace values and log all actions in the report list.
    """
    if isinstance(obj, dict):
        return {k: replace_values_with_logs(v, translations, report) for k, v in obj.items()}
    
    if isinstance(obj, list):
        return [replace_values_with_logs(item, translations, report) for item in obj]

    if isinstance(obj, str):
        english = obj.strip()
        
        # 1. Try exact match
        if english in translations:
            german = translations[english]
            report.append(f"✔ Replaced (Exact): '{english[:50]}...'")
            return german
        
        # 2. Try stripping HTML tags
        # Regex to remove <...> tags
        clean_english = re.sub(r'<[^>]+>', '', english).strip()
        
        # Also collapse multiple spaces that might result from stripping
        clean_english_normalized = re.sub(r'\s+', ' ', clean_english)
        
        if clean_english_normalized in translations:
            german = translations[clean_english_normalized]
            
            # Now we need to put the tags back!
            # We use the original 'english' (which has tags) and 'german' (which is plain text)
            german_with_tags = transfer_tags(english, german)
            
            report.append(f"✔ Replaced (Stripped HTML & Tags Restored): '{english[:50]}...' -> '{german_with_tags[:50]}...'")
            return german_with_tags
            
        # 3. Not found
        report.append(f"✖ Not found in Excel: '{english[:50]}...'")
        return obj

    return obj


def translate_and_verify(json_path, excel_path, output_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Load Excel translations
    translations = load_translation_excel(excel_path)

    report = []

    updated_json = replace_values_with_logs(data, translations, report)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(updated_json, f, indent=4, ensure_ascii=False)

    # split report into replaced and not-found lists
    replaced_lines = [r for r in report if r.startswith("✔")]
    not_found_lines = [r for r in report if r.startswith("✖")]

    print("\n============================")
    print(" TRANSLATION VERIFICATION ")
    print("============================\n")

    print("Found & Replaced:")
    if replaced_lines:
        for line in replaced_lines:
            print(line)
    else:
        print("  (none)")

    print("\nNot Found in Excel:")
    if not_found_lines:
        for line in not_found_lines:
            print(line)
    else:
        print("  (none)")

    print("\n============================")
    print(f"✔ Total Replaced: {len(replaced_lines)}")
    print(f"✖ Not Found in Excel: {len(not_found_lines)}")
    print("============================")



# Use 'en-gb-translated.json' as the source (English with tags)
# and 'Tleft.json' as the output
json_file = "testinput.json" 
excel_file = "german.xlsx"
output_file = "testoutput.json"

translate_and_verify(json_file, excel_file, output_file)
