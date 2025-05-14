#most imp python file to perform semantic search
import weaviate
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

# Load Weaviate client
client = weaviate.Client(
    url=os.getenv("WEAVIATE_URL"),
    auth_client_secret=weaviate.auth.AuthApiKey(api_key=os.getenv("WEAVIATE_API"))
)

class SemanticSearchClass:
    def __init__(self):
        #self is a param which is reference to curr instance of class
        # __init__() fn automatically initiliazes object attributes when obj is made
        self.device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.weaviate_client = self._init_weaviate_client()
        self.tokenizer , self.model=self._load_model()

    #load model
    def _load_model(self):
        tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
        model = AutoAdapterModel.from_pretrained('allenai/specter2_base')
        model.load_adapter("allenai/specter2", source="hf", set_active=True)
        return tokenizer, model.to(self.device)

    #starting the client
    def _init_weaviate_client(self)->weaviate.Client:
        try:
            client=weaviate.Client(url=os.getenv("WEAVIATE_URL"),
            auth_client_secret=weaviate.auth.AuthApiKey(api_key=os.getenv("WEAVIATE_API")))
            if client.is_ready():
                return client
        except Exception as e:
            logger.error("Failed operation to initiate conncetion with client")
            raise
    
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
            result = self.weaviate_client.query.get(
                "PaperChunk",
                ["text", "filename", "page", "_additional {certainty}"]
            ).with_near_vector({
                "vector": query_vector,
                "certainty": certainty_threshold
            }).with_limit(top_k).do()
            
            return self.search_results(result)
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    #present results

    def search_results(self, raw_res:Dict)->List[Dict[str,Any]]:
        items = raw_res.get("data", {}).get("Get", {}).get("PaperChunk", [])
        
        return [{
            "text": item["text"],
            "source": item["filename"],
            "page": item["page"],
            "confidence": item["_additional"]["certainty"],
            "full_text": item["text"]
        } for item in items]
    
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
        return res.json()["choices"][0]["message"]["content"]
        


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
#                     certainty_threshold=0.65
#                 )      
#             if not results:
#                 print("\nNo relevant evidence found in database")
#                 continue
            
#             print(f"\nFound {len(results)} relevant results:")
#             for idx, result in enumerate(results, 1):
#                 print(f"\nResult {idx}:")
#                 print(f"Source: {result['source']} (Page {result['page']})")
#                 print(f"Confidence: {result['confidence']:.2%}")
#                 print(f"Excerpt: {result['text'][:200]}...")
            
#             mistral_response=search_engine.generate_answer(query,results)
#             print("In conclusion: ")
#             print(mistral_response)
#         except KeyboardInterrupt:
#             print("\nOperation cancelled by user")
#             break
# if __name__=="__main__":
#     main()