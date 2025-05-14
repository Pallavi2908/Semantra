from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import SemanticSearchClass  # importing your class
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Allow CORS (for frontend to call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_engine = SemanticSearchClass()

class Query(BaseModel):
    query: str

@app.post("/query")
async def handle_query(data: Query):
    print(f"Received query: {repr(data.query)}")
    print("Query received")  # log message
    query = data.query.strip()
    if not query:
        return {"error": "Empty query"}

    results = search_engine.search_medical_claims(
        query=query,
        top_k=10,
        certainty_threshold=0.65
    )
    if not results:
        return {"message": "No relevant evidence found."}

    answer = search_engine.generate_answer(query, results)
    return {"answer": answer, "chunks": results}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API!"}
