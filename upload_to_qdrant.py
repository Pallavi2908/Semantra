#this script uploads  merged_chunks.json to Qdrant. Migrating to Qdrant:


# upload_to_qdrant.py

import json,os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
# from qdrant_client.http.models import PointStruct, WriteRequest
from dotenv import load_dotenv
from uuid import uuid4

COLLECTION_NAME = "chunk_data"
DATA_PATH = "final_Jul.json"
load_dotenv()

def get_qdrant_client():
    client = QdrantClient(
        url=os.getenv('QDRANT_URL'),
        api_key=os.getenv('QDRANT_API'),
    )
    return client
def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def convert_to_points(data):
    points = []
    for i, item in enumerate(data):
        if not item.get("embedding") or not isinstance(item["embedding"], list):
            print(f"❌ Skipping item {i} — Missing or invalid 'embedding'")
            continue

        if len(item["embedding"]) != 768:
            print(f"❌ Skipping item {i} — Vector length is {len(item['embedding'])}, expected 768")
            continue

        points.append(PointStruct(
            id=str(uuid4()),
            vector=item["embedding"],
            payload={
                "chunk_id": item["chunk_id"],
                "text": item.get("text", ""),
                "filename": item["filename"],
                "page": item.get("page", -1)
            }
        ))

    print(f"🔎 convert_to_points → returning {len(points)} valid points")
    return points

def upload(points):
    client = get_qdrant_client()
    print("📡 Reached upload_points() call")

    client.upload_points(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )
    print(f"✅ Uploaded {len(points)} points to Qdrant.")


if __name__ == "__main__":
    data = load_data()
    points = convert_to_points(data)
    upload(points)
