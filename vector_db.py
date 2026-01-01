import os
import json
import time
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load Env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY missing.")
    exit(1)
if not PINECONE_API_KEY:
    print("Error: PINECONE_API_KEY missing. Please add it to .env")
    exit(1)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Configure Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "resume-bullets"

def get_embedding(text):
    # Use Gemini's text-embedding-004
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
            title="Resume Bullet Point"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error embedding text: {e}")
        return None

import traceback

def main():
    try:
        # 1. Setup Index
        print(f"Using Key: {PINECONE_API_KEY[:10]}...") 
        
        # Get index names safely for V5
        indexes_response = pc.list_indexes()
        try:
            if hasattr(indexes_response, 'names'):
                existing_indexes = indexes_response.names()
            else:
                 # Fallback for some versions
                existing_indexes = [i.name for i in indexes_response]
        except:
            existing_indexes = []
            
        print(f"Indexes found: {existing_indexes}")
        
        if INDEX_NAME not in existing_indexes:
            print(f"Creating Pinecone Index: {INDEX_NAME}...")
            try:
                pc.create_index(
                    name=INDEX_NAME,
                    dimension=768, # Gemini 004 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                time.sleep(15) # Wait for init
            except Exception as e:
                print(f"Error creating index (Free Tier limit?): {e}")
                # Try to use existing if creation fails
                pass
        
        index = pc.Index(INDEX_NAME)
        
        # 2. Load Data
        with open('augmented_resumes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        vectors_to_upsert = []
        
        print("Generating Embeddings...")
        
        # Process Domains
        for domain, content in data.items():
            # Combine Real + Synthetic
            real_pts = content.get("real", [])
            synth_pts = content.get("synthetic", [])
            all_pts = real_pts + synth_pts
            
            print(f"  > {domain}: {len(all_pts)} points")
            
            for i, text in enumerate(all_pts):
                # Generate ID
                vector_id = f"{domain}_{i}"
                
                # Embed
                embedding = get_embedding(text)
                if not embedding:
                    continue
                    
                # Metadata
                metadata = {
                    "text": text,
                    "domain": domain,
                    "type": "real" if i < len(real_pts) else "synthetic"
                }
                
                vectors_to_upsert.append((vector_id, embedding, metadata))
                
                # Batch Upsert (every 50)
                if len(vectors_to_upsert) >= 50:
                    index.upsert(vectors=vectors_to_upsert)
                    vectors_to_upsert = []
                    print(f"    Upserted batch for {domain}...")
                    time.sleep(1) # Rate limit nice-ness

        # Final Batch
        if vectors_to_upsert:
            index.upsert(vectors=vectors_to_upsert)
            print("    Upserted final batch.")

        print("\nSUCCESS: All data stored in Pinecone!")
        stats = index.describe_index_stats()
        print(stats)

    except Exception as e:
        print("\nCRITICAL ERROR:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
