import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
from humanizer import humanize_bullet

# Load Environment Variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY not found in .env")
    exit(1)

# Configure Groq
client = Groq(api_key=GROQ_API_KEY)
# Using Llama 3.3 70B as requested
MODEL_NAME = "llama-3.3-70b-versatile"

# Filter domains as requested
TARGET_DOMAINS = ["IT", "Product"]

def generate_bullets(domain, seeds, count=20):
    seed_text = "\n".join([f"- {s}" for s in seeds[:5]]) 
    
    prompt = f"""
    You are an expert Resume Writer for Top Tech Companies.
    JOB: Generate {count} HIGH-QUALITY resume bullet points for domain: "{domain}".
    STYLE: Use Action Verbs + Context + Metrics (Numbers, %, $).
    EXAMPLES:
    {seed_text}
    
    INSTRUCTIONS:
    1. Generate {count} NEW, UNIQUE bullets.
    2. STAR method.
    3. MUST have metrics.
    4. Output format: Just the bullet text, starting with "- ".
    """
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that writes perfect resume bullet points."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        text = completion.choices[0].message.content
        
        # Clean up response
        new_bullets = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                clean_line = line[2:].strip()
                new_bullets.append(clean_line)
            elif len(line) > 10 and line[0].isdigit():
                    parts = line.split(' ', 1)
                    if len(parts) > 1:
                        new_bullets.append(parts[1].strip())
        
        return new_bullets
            
    except Exception as e:
        print(f"    ! Error generating for {domain}: {e}")
        return []

def main():
    # 1. Load Data
    data_structure = {}
    
    if os.path.exists('augmented_resumes.json'):
         with open('augmented_resumes.json', 'r', encoding='utf-8') as f:
            data_structure = json.load(f)
    else:
         with open('cleaned_resumes.json', 'r', encoding='utf-8') as f:
            raw = json.load(f)
            for d, pts in raw.items():
                data_structure[d] = {"real": pts, "synthetic": []}

    # 2. Iterate Domains
    for domain in TARGET_DOMAINS:
        if domain not in data_structure:
            continue

        real_count = len(data_structure[domain]['real'])
        
        # Check if already augmented (threshold check)
        existing_synthetic = data_structure[domain].get('synthetic', [])
        if len(existing_synthetic) > 50: 
             print(f"\nSkipping {domain} (Enough synthetic data: {len(existing_synthetic)})")
             continue
             
        print(f"\nProcessing Domain: {domain}")
        
        seeds = data_structure[domain].get('real', [])
        context_seeds = seeds if seeds else []
        
        domain_new_points = []
        # Groq is fast, let's do bigger batches
        for i in range(2): 
            print(f"  > Batch {i+1}/2...")
            new_points = generate_bullets(domain, context_seeds, count=25)
            
            # HUMANIZE SYNTHETIC POINTS
            humanized_points = [humanize_bullet(p) for p in new_points]
            domain_new_points.extend(humanized_points)
            
            # Groq rate limits are generous but let's be safe
            time.sleep(2) 
            
        print(f"  > Generated {len(domain_new_points)} new points.")
        
        # Append to SYNTHETIC list
        data_structure[domain]['synthetic'].extend(domain_new_points)
        
        # SAVE INCREMENTALLY
        with open('augmented_resumes.json', 'w', encoding='utf-8') as f:
            json.dump(data_structure, f, indent=2, ensure_ascii=False)
        print(f"  [Saved progress for {domain}]")

    print("\nSUCCESS: Saved all to augmented_resumes.json")
    
    # Stats
    total_real = sum(len(v['real']) for v in data_structure.values())
    total_synth = sum(len(v['synthetic']) for v in data_structure.values())
    print(f"Total Database: {total_real} Real, {total_synth} Synthetic")

if __name__ == "__main__":
    main()
