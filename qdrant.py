#originally weaviate_collections.py
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API'),
)

try:
    print("Connected!")
except Exception as e:
    print("some error incurred",e)

def init_collection(qdrant_client, collection_name="chunk_data",vector_size=768):
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )
    


if __name__ == "__main__":
    init_collection(qdrant_client)
