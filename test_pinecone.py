import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")

print(f"Key loaded: {str(api_key)[:10]}...")

try:
    pc = Pinecone(api_key=api_key)
    print("Client initialized.")
    indexes = pc.list_indexes()
    print(f"Indexes: {indexes}")
except Exception as e:
    print(f"Error: {e}")
