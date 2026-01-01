import json
import os
import re
import random

# Logic adapted from USER's removeBIGnumbers.py
def process_bullet(text):
    # Synonyms to break repetitive sentence structures
    connectors = ["yielding", "driving", "leading to", "facilitating", "contributing to"]
    
    # 1. JITTER NUMBERS (Avoid round numbers)
    text = re.sub(r'(\d+)%', lambda m: f"{int(m.group(1)) + random.randint(-1, 1)}%", text)
    
    # 2. REVENUE BALANCER (The "Anti-Unicorn" Logic)
    # Target INR patterns: "totaling Rs. 4.2 Cr", "generating Rs. 45 Lakhs"
    # Target USD patterns: "generating $500,000"
    
    financial_pattern = r', (totaling|yielding|resulting in|generating|saving the company|contributing to) (an additional )?((Rs\. [\d\.]+ (Cr|Lakhs))|(\$[\d,]+( million)?))( in revenue( growth)?)?'
    
    match = re.search(financial_pattern, text, re.IGNORECASE)
    
    if match:
        # 60% chance to REMOVE the financial phrase completely to sound less "salesy"
        if random.random() > 0.4: 
            text = re.sub(financial_pattern, '', text, flags=re.IGNORECASE)
            # Cleanup trailing punctuation
            text = text.strip()
            if not text.endswith('.'):
                text += "."
        else:
            # If checking USD, Indianize it (fallback)
            if "$" in match.group(0):
                 def convert_to_rs(m):
                    raw_str = m.group(0)
                    if "million" in raw_str:
                        base = float(re.search(r'[\d\.]+', raw_str).group()) * 1_000_000
                    else:
                        base = int(re.sub(r'[$,]', '', raw_str))
                    
                    val = base * 85
                    if val >= 10_000_000:
                        return f"Rs. {val/10_000_000:.2f} Cr"
                    else:
                        return f"Rs. {int(val/100_000)} Lakhs"

                 text = re.sub(r'\$[\d,]+(\s?million)?', convert_to_rs, text)

    # 3. VARIETY INJECTION
    if "resulting in" in text:
        text = text.replace("resulting in", random.choice(connectors), 1)
    
    # 4. TECH INJECTION
    text = text.replace("market trends", "market signals (Google Trends/Nielsen)")
    text = text.replace("product roadmap", "strategic roadmap (Jira)")

    return text

def main():
    file_path = 'augmented_resumes.json'
    if not os.path.exists(file_path):
        print("Error: augmented_resumes.json not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    
    # Apply to Product Synthetic Data
    if 'Product' in data and 'synthetic' in data['Product']:
        print(f"Optimizing Product Domain - {len(data['Product']['synthetic'])} points...")
        original_points = data['Product']['synthetic']
        
        new_points = []
        for p in original_points:
            new_p = process_bullet(p)
            new_points.append(new_p)
            if new_p != p:
                updated_count += 1
                
        data['Product']['synthetic'] = new_points
        
    # Apply REVENUE/VARIETY logic to IT Synthetic too (skipping Product-specific tech replacement if not found)
    # The function is safe to run on IT as replacements won't match
    if 'IT' in data and 'synthetic' in data['IT']:
        print(f"Optimizing IT Domain - {len(data['IT']['synthetic'])} points...")
        original_points = data['IT']['synthetic']
        new_points = []
        for p in original_points:
            # We use the same function, tech terms won't match so it's fine
            new_p = process_bullet(p)
            new_points.append(new_p)
            if new_p != p:
                updated_count += 1
        data['IT']['synthetic'] = new_points

    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccess! Optimized {updated_count} bullet points (Revenue Balancing + Variety).")

if __name__ == "__main__":
    main()
