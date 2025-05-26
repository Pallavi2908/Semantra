import weaviate
import json, os
from dotenv import load_dotenv
import uuid

# Load env and connect
load_dotenv()
client = weaviate.Client(
    url=os.getenv('WEAVIATE_URL'),
    auth_client_secret=weaviate.auth.AuthApiKey(api_key=os.getenv('WEAVIATE_API'))
)

# Load merged JSON
with open("merged_embeddings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

client.batch.configure(batch_size=100, callback=lambda res: print("🧾 Batch result:", res))

skipped = 0

with client.batch as batch:
    for i, item in enumerate(data):
        if "embedding" not in item or not isinstance(item["embedding"], list):
            print(f"❌ Skipping {item.get('chunk_id')} — missing or invalid embedding")
            skipped += 1
            continue

        vector = item["embedding"]
        if len(vector) != 768:
            print(f"❌ Skipping {item.get('chunk_id')} — vector not 768-dim")
            skipped += 1
            continue

        chunk_id_raw = item.get("chunk_id", None)

        # Try to convert to UUID or generate a new one
        try:
            chunk_uuid = str(uuid.UUID(chunk_id_raw)) if chunk_id_raw else str(uuid.uuid4())
        except:
            chunk_uuid = str(uuid.uuid4())

        properties = {
            "chunk_id": chunk_id_raw or chunk_uuid,
            "filename": item.get("filename", "unknown"),
            "text": item.get("text", ""),
            "page": int(item.get("page", -1))
        }

        batch.add_data_object(
            data_object=properties,
            class_name="ChunkData",
            uuid=chunk_uuid,
            vector=vector
        )

        if i % 100 == 0:
            print(f"✅ Uploaded {i} chunks")

print(f"✅ Upload complete. Skipped {skipped} invalid entries.")
