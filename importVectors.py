import weaviate
import json, os 
from dotenv import load_dotenv

load_dotenv()
client = weaviate.Client(
    url = os.getenv('WEAVIATE_URL'),  # Replace with your Weaviate endpoint
    auth_client_secret=weaviate.auth.AuthApiKey(api_key=os.getenv('WEAVIATE_API')),  # Replace with your Weaviate instance API key
)

with open("processes.json","r",encoding="utf-8") as f:
    processed_data=json.load(f)

with open("vectors.json","r",encoding="utf-8") as f:
    embeddings=json.load(f)

lookup_dict={
    emb["filename"]: emb["embeddings"] for emb in embeddings
}

client.batch.configure(batch_size=100)

with client.batch as batch:
    for doc in processed_data:
        filename=doc["metadata"]["filename"]
        chunks=doc["chunks"]
        vectors=lookup_dict[filename]

        for chunk in chunks:
            chunk_id=chunk["chunk_id"]
            text=chunk["text"]
            page=chunk["page"]
            vector=vectors.get(chunk_id)

            properties={
                "chunk_id":chunk_id,
                "text": text,
                "filename": filename,
                "page": page
            }

            batch.add_data_object(properties,class_name="PaperChunk", vector=vector)