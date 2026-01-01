import os
import sys
import json
import traceback
from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "web", ".env")
load_dotenv(dotenv_path=env_path)

def parse_resume(file_path):
    try:
        # 1. Extract Text
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            print(json.dumps({"error": "No text extracted from PDF"}))
            return

        # 2. Call Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
             print(json.dumps({"error": "GROQ_API_KEY missing"}))
             return

        client = Groq(api_key=api_key)
        
        system_prompt = """
        You are an expert Resume Parser. 
        Extract the resume data from the text provided below into the following strict JSON format:
        {
            "profile": { "name": "", "email": "", "phone": "", "linkedin": "", "github": "", "website": "", "summary": "" },
            "experience": [ { "id": "uuid", "company": "", "role": "", "startDate": "", "endDate": "", "location": "", "bullets": [] } ],
            "projects": [ { "id": "uuid", "name": "", "description": "", "technologies": [], "link": "", "bullets": [] } ],
            "education": [ { "id": "uuid", "school": "", "degree": "", "field": "", "startDate": "", "endDate": "", "grade": "" } ],
            "responsibilities": [ { "id": "uuid", "title": "", "organization": "", "location": "", "startDate": "", "endDate": "", "description": "" } ],
            "achievements": [ "Achievement 1 with details", "Achievement 2 with details" ],
            "skills": []
        }
        
        SECTION HEADER MAPPINGS - Map these variations to our fields:
        
        EXPERIENCE (put in "experience"):
        - "Work Experience", "Professional Experience", "Employment History", "Career History"
        - "Work History", "Professional Background", "Experience", "Internships"
        - "Relevant Experience", "Industry Experience"
        
        EDUCATION (put in "education"):
        - "Education", "Academic Background", "Educational Qualifications", "Academic History"
        - "Degrees", "Schooling", "Academic Credentials"
        
        PROJECTS (put in "projects"):
        - "Projects", "Personal Projects", "Academic Projects", "Key Projects"
        - "Technical Projects", "Portfolio", "Side Projects"
        
        SKILLS (put in "skills"):
        - "Skills", "Technical Skills", "Core Competencies", "Key Skills"
        - "Expertise", "Proficiencies", "Technologies", "Tools & Technologies"
        
        ACHIEVEMENTS (put in "achievements"):
        - "Achievements", "Certifications", "Awards", "Honors"
        - "Accomplishments", "Courses", "Licenses", "Publications"
        - "Achievements & Certifications", "Awards & Honors"
        
        RESPONSIBILITIES (put in "responsibilities"):
        - "Positions of Responsibility", "Leadership", "Extracurriculars"
        - "Volunteer Work", "Community Involvement", "Activities"
        - "Leadership Experience", "Organizational Roles"
        
        Rules:
        - If a field is missing, use empty string or empty list. 
        - Do not invent data.
        - IMPORTANT for experience:
          * "role" = the job title (e.g. "Founders Office Intern", "Software Engineer", "Marketing Manager")
          * "company" = the company/startup name (e.g. "Pinch", "Google", "StampMyVisa")
          * Do NOT swap these - role is what you DO, company is WHERE you work
        - Return ONLY the raw JSON string. No markdown formatting.
        """

        completion = client.chat.completions.create(
            messages=[
                { "role": "system", "content": system_prompt },
                { "role": "user", "content": f"Resume Text:\n{text}" }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0,
            stream=False,
        )

        result = completion.choices[0].message.content
        
        # Clean result
        result = result.replace("```json", "").replace("```", "").strip()
        
        # Validate JSON
        parsed_json = json.loads(result)
        
        # Output to stdout
        print(json.dumps(parsed_json))

    except Exception as e:
        error_info = {
            "error": str(e),
            "trace": traceback.format_exc()
        }
        print(json.dumps(error_info))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
    else:
        parse_resume(sys.argv[1])
