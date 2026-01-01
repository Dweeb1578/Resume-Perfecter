import os
import google.generativeai as genai
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "web", ".env")
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY missing")
    exit(1)

genai.configure(api_key=api_key)

try:
    print("Testing Embedding Generation...")
    result = genai.embed_content(
        model="models/text-embedding-004",
        content="Hello world",
        task_type="retrieval_query"
    )
    print("Success! Embedding length:", len(result['embedding']))
except Exception as e:
    print("Error:", e)
