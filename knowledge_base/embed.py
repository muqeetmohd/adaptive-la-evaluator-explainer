import chromadb
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "all-MiniLM-L6-v2"
_COLLECTION_NAME = "linear_algebra"


def build_knowledge_base(chunks: list, persist_dir: str = "./chroma_db"):
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(_COLLECTION_NAME)
    model = SentenceTransformer(_MODEL_NAME)

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk["text"]).tolist()
        collection.add(
            ids=[f"{chunk['source']}_{i}"],
            embeddings=[embedding],
            documents=[chunk["text"]],
            metadatas=[{
                "tier": chunk["tier"],
                "source": chunk["source"],
                "topic": chunk["topic"],
            }],
        )
        if (i + 1) % 100 == 0:
            print(f"Ingested {i + 1} / {len(chunks)} chunks...")

    print(f"Done. Total chunks ingested: {len(chunks)}")
    return collection


def load_knowledge_base(persist_dir: str = "./chroma_db") -> chromadb.Collection:
    client = chromadb.PersistentClient(path=persist_dir)
    return client.get_collection(_COLLECTION_NAME)
