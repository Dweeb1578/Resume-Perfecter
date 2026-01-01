import json
import re

def clean_latex_string(text):
    if not text:
        return ""
    
    # 1. Escape & (except if it's already escaped)
    text = re.sub(r'(?<!\\)&', r'\&', text)
    
    # 2. Escape % (except if it's already escaped)
    text = re.sub(r'(?<!\\)%', r'\%', text)
    
    # 3. Escape $ (essential for your "single $" rule)
    text = re.sub(r'(?<!\\)\$', r'\$', text)
    
    # 4. Clean up weird whitespace/tabs
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def audit_dataset(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned_data = {}
    broken_lines = []

    for category, lines in data.items():
        cleaned_data[category] = []
        for line in lines:
            # Check for truncation (lines ending in specific ways)
            if line.endswith(' ') or line.count('{') > line.count('}'):
                broken_lines.append({"category": category, "text": line})
                continue
            
            cleaned_data[category].append(clean_latex_string(line))
            
    return cleaned_data, broken_lines

# EXECUTION
data_file = 'resume_bullets.json' # Your raw JSON
cleaned, broken = audit_dataset(data_file)

print(f"Cleaned {sum(len(v) for v in cleaned.values())} lines.")
print(f"Found {len(broken)} broken/truncated lines.")

# Save the clean version
with open('cleaned_resumes.json', 'w') as f:
    json.dump(cleaned, f, indent=2)