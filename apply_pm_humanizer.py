import json
import os
from humanizerPM import humanize_and_indianize

def main():
    file_path = 'augmented_resumes.json'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    
    # Target ONLY Product -> Synthetic
    if 'Product' in data and 'synthetic' in data['Product']:
        print(f"Processing Product Domain - {len(data['Product']['synthetic'])} points...")
        original_points = data['Product']['synthetic']
        
        new_points = []
        for p in original_points:
            # Check if likely already latex-escaped or processed?
            # humanize_and_indianize adds \% and \$ so we should be careful avoiding double escaping if run multiple times
            # But simpler is just to run it.
            new_p = humanize_and_indianize(p)
            new_points.append(new_p)
            
            if new_p != p:
                updated_count += 1
                
        data['Product']['synthetic'] = new_points

    # Save details
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccess! Updated {updated_count} Product bullet points with the Indian Humanizer.")

if __name__ == "__main__":
    main()
