import json
import os
from humanizer import humanize_bullet

def main():
    file_path = 'augmented_resumes.json'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    
    for domain, content in data.items():
        if 'synthetic' in content:
            print(f"Processing {domain} - {len(content['synthetic'])} points...")
            original_points = content['synthetic']
            
            # Apply humanizer
            humanized_points = [humanize_bullet(p) for p in original_points]
            
            # Check how many actually changed (optional, but good for logs)
            for o, h in zip(original_points, humanized_points):
                if o != h:
                    updated_count += 1
            
            content['synthetic'] = humanized_points

    # Save details
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccess! Updated {updated_count} synthetic bullet points with the latest humanizer logic.")

if __name__ == "__main__":
    main()
