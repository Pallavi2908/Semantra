import weaviate
import json, os
from dotenv import load_dotenv

load_dotenv()
client = weaviate.Client(
    url = os.getenv('WEAVIATE_URL'),  # Replace with your Weaviate endpoint
    auth_client_secret=weaviate.auth.AuthApiKey(api_key=os.getenv('WEAVIATE_API')),  # Replace with your Weaviate instance API key
)
with open("class.json","r") as f:
    class_obj=json.load(f)
    print("succesfully read")

client.schema.create_class(class_obj)