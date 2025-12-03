
import re

def transfer_tags(source, target):
    """
    Transfers HTML tags from source string to target string based on relative text position,
    snapping to the nearest word boundary to avoid breaking words.
    """
    # 1. Extract tags and their positions relative to the CLEAN text
    tags = []
    tag_matches = list(re.finditer(r'<[^>]+>', source))
    
    if not tag_matches:
        return target
        
    clean_source = ""
    last_idx = 0
    tags_to_insert = []
    current_clean_len = 0
    
    for match in tag_matches:
        text_segment = source[last_idx:match.start()]
        clean_source += text_segment
        current_clean_len += len(text_segment)
        
        tags_to_insert.append({
            'tag': match.group(0),
            'clean_pos': current_clean_len
        })
        last_idx = match.end()
        
    clean_source += source[last_idx:]
    source_len = len(clean_source)
    
    if source_len == 0:
        return target + "".join([t['tag'] for t in tags_to_insert])

    # 2. Calculate ratios and find positions in target
    target_len = len(target)
    target_insertions = [] 
    
    for tag_info in tags_to_insert:
        ratio = tag_info['clean_pos'] / source_len
        target_pos = int(round(ratio * target_len))
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
        
    # Sort by position
    target_insertions.sort(key=lambda x: x[0])
    
    # Construct result
    result = ""
    current_idx = 0
    
    for pos, tag in target_insertions:
        result += target[current_idx:pos]
        result += tag
        current_idx = pos
        
    result += target[current_idx:]
    
    return result

# Test Cases
tests = [
    ("Go <b>Now</b>", "Vaya Inmediatamente"),
    ("<b>Super</b>man", "Superhombre"),
    ("Click <a href='...'>Here</a>", "Haga clic aqui"),
    ("Ready to <span class='text-PrimaryBlue'>Transcend?</span>", "¿Listo para trascender?")
]

for s, t in tests:
    print(f"\nSource: {s}")
    print(f"Target: {t}")
    print(f"Result: {transfer_tags(s, t)}")
