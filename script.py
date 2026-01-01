import requests
import re
import time
import base64
import json

# CONFIGURATION
# GITHUB_TOKEN = os.getenv('GITHUB_TOKEN') # Use env var in production
GITHUB_TOKEN = '' # Placeholder - DO NOT COMMIT SECRETS
HEADERS = {}
if GITHUB_TOKEN:
    HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# DOMAIN DEFINITIONS
# (Domain Name, Job Titles, Top Companies)
DOMAINS = {
    "IT": (
        ["Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack", "DevOps"],
        ["Google", "Meta", "Amazon", "Microsoft", "Apple", "Netflix", "Uber", "Airbnb"]
    ),
    "Product": (
        ["Product Manager", "Product Owner", "Program Manager"],
        ["Uber", "Airbnb", "Stripe", "Google", "Meta", "Amazon"]
    ),
    "Marketing": (
        ["Marketing Manager", "Brand Manager", "Digital Marketing"],
        ["Nike", "Apple", "Coca-Cola", "Procter & Gamble", "Unilever", "PepsiCo"]
    ),
    "Core Electronics": (
        ["Hardware Engineer", "Electronics Engineer", "Embedded Systems"],
        ["NVIDIA", "Intel", "AMD", "Qualcomm", "Samsung", "Texas Instruments"]
    ),
    "Mechanical": (
        ["Mechanical Engineer", "Design Engineer", "Mechatronics"],
        ["Tesla", "SpaceX", "Boeing", "NASA", "Lockheed Martin", "Ford", "General Motors"]
    )
}

def is_high_quality(text):
    """
    Heuristics for a 'perfect' bullet point:
    1. Length > 60 chars (already in regex, but good to double check)
    2. Contains numbers/metrics (%, $, digits)
    3. Starts with a capital letter (implied by regex mostly)
    """
    if len(text) < 60:
        return False
    
    # Must contain a number or percentage or dollar sign (metrics)
    if not re.search(r'(\d+%|\$\d+|\d+)', text):
        return False
        
    return True

def clean_bullet(text):
    # Remove LaTeX commands, extra spaces, etc.
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('\\\\', '')
    text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text) # remove bold latex
    text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text) # remove italic latex
    return text

def scrape_domain(domain_name, roles, companies):
    print(f"\n--- SCRAPING DOMAIN: {domain_name} ---")
    
    unique_bullets = set()
    
    # SIMPLE STRATEGY: 
    # Query 1 Role + 1 Company at a time to avoid GitHub 256 char limit and 422 errors.
    # We will limit to the first 1 Role and top 3 Companies to ensure this runs in reasonable time.
    
    target_role = roles[0] 
    target_companies = companies[:3] 
    
    for company in target_companies:
        # Query: extension:tex "Software Engineer" "Google"
        query = f'extension:tex "{target_role}" "{company}"'
        print(f"  > Querying: {query}")
        
        url = f"https://api.github.com/search/code?q={query}&per_page=5" # Get top 5 files
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"    ! Error {response.status_code} - {response.text[:50]}")
            time.sleep(2)
            continue
            
        items = response.json().get('items', [])
        print(f"    Found {len(items)} files.")
        
        # Regex to find \item {...}
        pattern = r'\\(?:resumeItem|item)\s*\{([^}]{60,})\}'
        
        for item in items: 
            try:
                file_url = item['url']
                file_resp = requests.get(file_url, headers=HEADERS)
                if file_resp.status_code == 200:
                    content_b64 = file_resp.json().get('content', '')
                    raw_text = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
                    
                    found_matches = re.findall(pattern, raw_text, re.DOTALL)
                    for match in found_matches:
                        clean = clean_bullet(match)
                        if is_high_quality(clean):
                            unique_bullets.add(clean)
                
                time.sleep(0.5) 
            except Exception as e:
                print(f"    ! Failed to parse file: {e}")
                
        time.sleep(2) # Be kind to API
        
    return list(unique_bullets)

# MAIN EXECUTION
all_results = {}
stats = {}

print("Starting Multi-Domain Scrape...")
for domain, (roles, companies) in DOMAINS.items():
    bullets = scrape_domain(domain, roles, companies)
    all_results[domain] = bullets
    stats[domain] = len(bullets)
    print(f"  >>> Extracted {len(bullets)} high-quality bullets for {domain}")

# REPORTING
print("\n" + "="*40)
print("FINAL STATISTICS (Top 3 Companies/Domain)")
print("="*40)
print(f"{'DOMAIN':<20} | {'COUNT':<10}")
print("-" * 33)
for d, c in stats.items():
    print(f"{d:<20} | {c:<10}")
print("="*40)

# SAVING
output_file = 'resume_bullets.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\nSaved all data to {output_file}")
