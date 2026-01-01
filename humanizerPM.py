import re
import random
import json

def humanize_and_indianize(text):
    # 1. JITTER PERCENTAGES
    # Changes "30%" to "32%" or "28%" to avoid AI-looking round numbers
    def jitter_percent(match):
        val = int(match.group(1))
        jittered = val + random.randint(-3, 3)
        return f"{jittered}%"
    text = re.sub(r'(\d+)%', jitter_percent, text)

    # 2. CONVERT CURRENCY (USD -> INR) & FORMAT
    # Assumes synthetic data is in USD. Converts to Rs. Lakhs/Crores
    def convert_to_rs(match):
        raw_str = match.group(0)
        
        # Extract base USD value
        if "million" in raw_str:
            base_usd = float(re.search(r'[\d\.]+', raw_str).group()) * 1_000_000
        else:
            clean_str = re.sub(r'[$,]', '', raw_str)
            base_usd = int(clean_str)

        # Rate: ~85 INR per USD + random variance for realism
        rate = 85 + random.randint(-2, 2)
        inr_val = base_usd * rate
        
        # Format Logic: > 1 Crore uses "Cr", else "Lakhs"
        if inr_val >= 10_000_000:
            crores = inr_val / 10_000_000
            # e.g., "Rs. 4.2 Cr"
            return f"Rs. {crores:.2f} Cr" 
        else:
            lakhs = int(inr_val / 100_000)
            # e.g., "Rs. 45 Lakhs"
            return f"Rs. {lakhs} Lakhs"

    # Regex captures "$1 million", "$500,000", "$100k"
    text = re.sub(r'\$[\d,]+(\s?million)?', convert_to_rs, text)

    # 3. INJECT INDIAN TECH CONTEXT
    # Replaces generic terms with things specific to the Indian startup/tech ecosystem
    replacements = {
        "market trends": "Tier-1 & Tier-2 city adoption patterns",
        "product roadmap": "strategic roadmap (Jira/Linear)",
        "competitor data": "competitive benchmarking",
        "customer feedback": "user feedback (via Intercom/Razorpay logs)",
        "sales and marketing": "Sales and Growth teams",
        "stakeholders": "cross-functional stakeholders",
        "go-to-market strategy": "GTM strategy across APAC regions"
    }
    
    for generic, specific in replacements.items():
        text = text.replace(generic, specific)

    # 4. LATEX SAFETY CHECK
    # Escape special characters just in case
    text = text.replace("%", "\\%") 
    text = text.replace("$", "\\$")
    
    return text

# --- TEST RUN ---
synthetic_data = [
    "Collaborated with teams to launch a product, saving the company $500,000.",
    "Driven a 39% increase in market share and $1 million in revenue.",
    "Resulting in a 25% reduction in costs, totaling $200,000."
]

print("--- GOD-TIER INDIAN RESUME BULLETS ---\n")
for line in synthetic_data:
    final_bullet = humanize_and_indianize(line)
    # Wrap in LaTeX \item format
    print(f"\\item {{{final_bullet}}}")
    print("-" * 40)