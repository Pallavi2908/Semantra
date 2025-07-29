#most imp python file to perform semantic search
import json 
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import logging, os,requests, torch
from transformers import AutoTokenizer
from adapters import AutoAdapterModel
from typing import List, Dict, Any


from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

#setting up logging 
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

class SemanticSearchClass:
    # def __init__(self):  
    #     #self is a param which is reference to curr instance of class
    #     # __init__() fn automatically initiliazes object attributes when obj is made
    #     self.qdrant_client = self._init_qdrant_client()
    #     self.tokenizer, self.model = self._load_model()
    #     self.collection_name = "chunk_data"
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # ✅ define this first
        self.qdrant_client = self._init_qdrant_client()
        self.tokenizer, self.model = self._load_model()
        self.collection_name = "chunk_data"


    #load model
    def _load_model(self):
        tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
        model = AutoAdapterModel.from_pretrained('allenai/specter2_base')
        model.load_adapter("allenai/specter2", source="hf", set_active=True)
        return tokenizer, model.to(self.device)

    #starting the client
    def _init_qdrant_client(self) -> QdrantClient:
        return QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API")
        )
    #generate embedding
    def generate_input_embedding(self, query: str) -> List[float]:
        inputs=self.tokenizer(query, padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=512).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
    
    #semantic search fn
    def search_medical_claims(
        self,
        query: str,
        top_k: int = 10,
        certainty_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        try:
            query_vector = self.generate_input_embedding(query)
            results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
            )

            return self.search_results(results, certainty_threshold)
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    #present results

    def search_results(self, raw_hits: List[Dict[str, Any]], score_threshold: float) -> List[Dict[str, Any]]:
        return [
            {
                "text": hit.payload["text"],
                "source": hit.payload["filename"],
                "page": hit.payload["page"],
                "confidence": hit.score,
                "full_text": hit.payload["text"]
            }
            for hit in raw_hits if hit.score >= score_threshold
        ]

    def generate_answer(self, query, search_results: list)->str:
        evidence="\n\n".join([
           f"Source: {chunk['source']} (Page {chunk['page']})\n"
           f"Excerpt: {chunk['text']}"
            for chunk in search_results
       ])
        with open("context.md","r",encoding="utf-8") as f:
            prompt = f.read()
        mistral_api=os.getenv("MISTRAL_API")
        model="mistral-large-latest" 
        headers={
            "Authorization": f"Bearer {mistral_api}",
            "Content-Type": "application/json"
        }
        messages=[
            {
                "role":"system",
                "content": prompt,
            },
            {
                "role":"user",
                "content":(
                    f"Medical query: {query}\n\n"
                    f"Context:\n{evidence}"
                )
            }
        ]

        res=requests.post(
            url="https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json={
                "model" : model,
                "temperature" : 0.2,
                "messages" : messages,
                "frequency_penalty": 0
            }
        )
        try:
            data = res.json()
            if "choices" not in data:
                print("🚨 ERROR: Unexpected API response")
                print(data)  # Log the full JSON
                return "Something went wrong. Check API key or endpoint."

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"🚨 Failed to parse response: {e}")
            print("Raw response:", res.text)
            return "Model failed to respond properly."

        


###################################################
# Uncomment main() to run application in CLI and run `python main.py`

# def main():
#     search_engine=SemanticSearchClass()
#     print("What's your argument")

#     while True:
#         try:
#             query=input("\nEnter your medical query:").strip()
#             if query.lower() == 'exit':
#                 break
#             if not query:
#                 continue

#             results = search_engine.search_medical_claims(
#                     query,
#                     top_k=10,
#                     certainty_threshold=0.5
#                 )      
#             if not results:
#                 print("\nNo relevant evidence found in database")
#                 continue
            
#             # print(f"\nFound {len(results)} relevant results:")
#             for idx, result in enumerate(results, 1):
#                 # print(f"\nResult {idx}:")
#                 # print(f"Source: {result['source']} (Page {result['page']})")
#                 # print(f"Confidence: {result['confidence']:.2%}")
#                 print("Excerpt:", result['text'][:300], query)  # highlight query words

            
#             mistral_response=search_engine.generate_answer(query,results)
#             # print("In conclusion: ")
#             print(mistral_response)
#         except KeyboardInterrupt: 
#             print("\nOperation cancelled by user")
#             break
# if __name__=="__main__":
#     main()