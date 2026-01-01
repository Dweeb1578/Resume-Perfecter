import re
import random

# PASTE YOUR FULL 100+ LIST HERE
raw_bullets = [
    "Collaborated with cross-functional teams to launch a new product line, achieving a 97% customer satisfaction rate and a 27% reduction in production costs, saving the company $500,000.",
    "Analyzed market trends and competitor data to inform product roadmap decisions, driving a 39% increase in market share and a 19% increase in revenue growth, totaling $800,000.",
    # ... add all 100 lines here ...
]

def batch_process_resumes(bullets):
    processed = []
    
    # Synonyms to break repetitive sentence structures
    connectors = ["yielding", "driving", "leading to", "facilitating", "contributing to"]
    
    for text in bullets:
        # 1. JITTER NUMBERS (Avoid round numbers)
        text = re.sub(r'(\d+)%', lambda m: f"{int(m.group(1)) + random.randint(-3, 3)}%", text)
        
        # 2. REVENUE BALANCER (The "Anti-Unicorn" Logic)
        # We only want ~40% of bullets to have money. 
        # For the rest, we strip the money part to focus on the operational win.
        has_money = re.search(r'(totaling|resulting in|generating) (an additional )?\$[\d,]+( million)?( in revenue)?', text)
        
        if has_money:
            if random.random() > 0.4: # 60% chance to REMOVE money
                # Strip the money phrase from the end
                # e.g., ", totaling $500,000." -> "."
                text = re.sub(r', (totaling|resulting in|generating) (an additional )?\$[\d,]+( million)?( in revenue( growth)?)?', '', text)
            else:
                # 40% chance to KEEP money, but Indianize it
                def convert_to_rs(match):
                    raw_str = match.group(0)
                    if "million" in raw_str:
                        base = float(re.search(r'[\d\.]+', raw_str).group()) * 1_000_000
                    else:
                        base = int(re.sub(r'[$,]', '', raw_str))
                    
                    # Convert to INR (approx 85)
                    val = base * 85
                    if val >= 10_000_000:
                        return f"Rs. {val/10_000_000:.2f} Cr"
                    else:
                        return f"Rs. {int(val/100_000)} Lakhs"

                text = re.sub(r'\$[\d,]+(\s?million)?', convert_to_rs, text)

        # 3. VARIETY INJECTION
        # Replace "resulting in" with synonyms so it doesn't sound robotic
        if "resulting in" in text:
            text = text.replace("resulting in", random.choice(connectors), 1)

        # 4. TECH INJECTION (Simple mapping)
        text = text.replace("market trends", "market signals (Google Trends/Nielsen)")
        text = text.replace("product roadmap", "strategic roadmap (Jira)")
        
        processed.append(text)

    return processed

# RUN IT
fixed_list = batch_process_resumes(raw_bullets)

print(f"--- PROCESSED {len(fixed_list)} BULLETS ---")
for line in fixed_list[:5]: # Print first 5 to check
    print(f"\\item {{{line}}}")
    print("---")