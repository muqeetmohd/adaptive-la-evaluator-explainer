import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from knowledge_base.embed import load_knowledge_base
from knowledge_base.topics import TOPIC_LIST
from diagnostic.diagnostic import QUESTIONS
from pipeline import run_session

app = FastAPI(title="Adaptive LA Explainer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading embedding model...")
_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Loading ChromaDB collection...")
try:
    _collection = load_knowledge_base()
    print("Knowledge base loaded.")
except Exception as e:
    _collection = None
    print(f"WARNING: Could not load knowledge base: {e}")


class SessionRequest(BaseModel):
    user_query: str
    diagnostic_responses: list
    topic: str


@app.get("/api/topics")
def get_topics():
    return {"topics": TOPIC_LIST}


@app.get("/api/questions")
def get_questions():
    return {"questions": QUESTIONS}


@app.post("/api/session")
def run_session_endpoint(req: SessionRequest):
    if _collection is None:
        raise HTTPException(status_code=503, detail="Knowledge base not loaded.")
    try:
        result = run_session(
            user_query=req.user_query,
            diagnostic_responses=req.diagnostic_responses,
            topic=req.topic,
            collection=_collection,
            embed_model=_model,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
