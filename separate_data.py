import json
import os

def main():
    # Load Real Data
    with open('cleaned_resumes.json', 'r', encoding='utf-8') as f:
        real_data = json.load(f)

    # Load Mixed Data (Real + Synthetic)
    if os.path.exists('augmented_resumes.json'):
        with open('augmented_resumes.json', 'r', encoding='utf-8') as f:
            mixed_data = json.load(f)
    else:
        mixed_data = real_data # Fallback if no specific augmented file yet

    structured_data = {}

    for domain in real_data.keys():
        real_points = real_data.get(domain, [])
        mixed_points = mixed_data.get(domain, [])
        
        # Identify Synthetic (points in Mixed but not in Real)
        # Using sets for easy subtraction, but need to be careful with exact string matching
        real_set = set(real_points)
        synthetic_points = [p for p in mixed_points if p not in real_set]
        
        structured_data[domain] = {
            "real": real_points,
            "synthetic": synthetic_points
        }

    # Save new structure
    with open('augmented_resumes.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2, ensure_ascii=False)

    print("Successfully separated Real vs Synthetic data in augmented_resumes.json")
    
    # Stats
    for d, counts in structured_data.items():
        print(f"{d}: {len(counts['real'])} Real, {len(counts['synthetic'])} Synthetic")

if __name__ == "__main__":
    main()
