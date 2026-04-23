import chromadb
from sentence_transformers import SentenceTransformer


def retrieve_chunks(
    query: str,
    tier: int,
    topic: str,
    collection: chromadb.Collection,
    model: SentenceTransformer,
    top_k: int = 5,
) -> list:
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"$and": [{"tier": tier}, {"topic": topic}]},
        include=["documents", "metadatas"],
    )

    chunks = _parse_results(results)

    if len(chunks) < 3:
        fallback = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"tier": tier},
            include=["documents", "metadatas"],
        )
        chunks = _parse_results(fallback)

    return chunks


def _parse_results(results: dict) -> list:
    chunks = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    for doc, meta in zip(docs, metas):
        chunks.append({
            "text": doc,
            "source": meta.get("source", ""),
            "tier": meta.get("tier", ""),
            "topic": meta.get("topic", ""),
        })
    return chunks


def format_chunks_for_prompt(chunks: list) -> str:
    lines = []
    for i, chunk in enumerate(chunks, start=1):
        lines.append(
            f"[{i}] (Source: {chunk['source']}, Topic: {chunk['topic']})\n{chunk['text']}"
        )
    return "\n\n".join(lines)
