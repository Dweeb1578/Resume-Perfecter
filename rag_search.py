import os
import sys
import json
import google.generativeai as genai
from pinecone import Pinecone
from dotenv import load_dotenv

# Load Env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "web", ".env")
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not GEMINI_API_KEY or not PINECONE_API_KEY:
    print(json.dumps({"error": "Missing API Keys"}))
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "resume-bullets"

def search(query, top_k=5):
    try:
        # 1. Embed Query
        embedding_result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        vector = embedding_result['embedding']

        # 2. Query Pinecone
        index = pc.Index(INDEX_NAME)
        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )

        # 3. Format Results
        matches = []
        for match in results.matches:
            matches.append({
                "text": match.metadata.get("text", ""),
                "score": match.score,
                "domain": match.metadata.get("domain", "general")
            })

        print(json.dumps(matches))

    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No query provided"}))
    else:
        query_text = sys.argv[1]
        search(query_text)
