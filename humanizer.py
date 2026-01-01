import re
import random

def humanize_bullet(text):
    # 1. Jitter Percentages: Change "70%" to something like "72%"
    def jitter_percent(match):
        val = int(match.group(1))
        # Add/subtract a small random amount to avoid "round number" syndrome
        jittered = val + random.randint(-4, 3) 
        return f"{jittered}%"
    
    text = re.sub(r'(\d+)%', jitter_percent, text)

    # 2. Jitter Large Numbers: Change "150+" to "164"
    def jitter_count(match):
        val = int(match.group(1))
        jittered = val + random.randint(3, 17)
        return str(jittered)
    
    text = re.sub(r'(\d+)\+', jitter_count, text)

    # 3. Inject Technical Friction/Context
    # This dictionary maps generic AI words to specific, high-value tech stacks
    replacements = {
        "monitoring tools": "Prometheus and Grafana stack",
        "CI/CD pipelines": "GitLab CI/CD and Jenkins pipelines",
        "automated patching solution": "Ansible-driven automated patching workflow",
        "cloud infrastructure on AWS": "multi-region AWS architecture using Terraform",
        "Linux servers": "RHEL and Ubuntu instances",
        "vulnerability assessments": "OWASP ZAP vulnerability scans",
        "network routing and switching": "BGP routing and Cisco Nexus switching"
    }
    
    for generic, specific in replacements.items():
        text = text.replace(generic, specific)
        
    return text

# Example Test
raw_point = "Implemented an automated patching solution across 150+ Linux servers, reducing manual effort by 70%."
print(f"Before: {raw_point}")
print(f"After:  {humanize_bullet(raw_point)}")