import chromadb
from sentence_transformers import SentenceTransformer

from diagnostic.diagnostic import run_diagnostic
from retrieval.retrieve import retrieve_chunks, format_chunks_for_prompt
from generation.prompt import build_prompt
from generation.generate import generate_explanation


def run_session(
    user_query: str,
    diagnostic_responses: list,
    topic: str,
    collection: chromadb.Collection,
    embed_model: SentenceTransformer,
) -> dict:
    diagnostic_result = run_diagnostic(diagnostic_responses)
    tier = diagnostic_result["tier"]
    misconception = diagnostic_result["misconception"]

    chunks = retrieve_chunks(user_query, tier, topic, collection, embed_model)
    chunks_text = format_chunks_for_prompt(chunks)

    prompt_messages = build_prompt(tier, misconception, chunks_text, user_query)
    explanation = generate_explanation(prompt_messages)

    sources_used = list({chunk["source"] for chunk in chunks})

    return {
        "tier": tier,
        "misconception": misconception,
        "chunks_retrieved": len(chunks),
        "explanation": explanation,
        "sources_used": sources_used,
    }
