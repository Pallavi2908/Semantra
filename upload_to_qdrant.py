#this script uploads  merged_chunks.json to Qdrant. Migrating to Qdrant:


# upload_to_qdrant.py

import json,os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
# from qdrant_client.http.models import PointStruct, WriteRequest
from dotenv import load_dotenv
from uuid import uuid4

COLLECTION_NAME = "chunk_data"
DATA_PATH = "merged_chunks.json"
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

    for item in data:
        if not item.get("embedding") or not item.get("text"):
            continue  # skip incomplete data

        points.append(PointStruct(
            id=str(uuid4()),
            vector=item["embedding"],
            payload={
                "chunk_id": item["chunk_id"],
                "text": item["text"],
                "filename": item["filename"],
                "page": item["page"]
            }
        ))

    return points

def upload(points):
    client = get_qdrant_client()
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
