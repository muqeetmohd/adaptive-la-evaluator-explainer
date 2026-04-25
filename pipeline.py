import chromadb
from sentence_transformers import SentenceTransformer

from diagnostic.diagnostic import run_diagnostic
from retrieval.retrieve import retrieve_chunks, format_chunks_for_prompt
from generation.prompt import build_prompt
from generation.generate import generate_explanation, generate_explanation_stream


def _prepare_session(
    user_query: str,
    diagnostic_responses: list,
    topic: str,
    collection,
    embed_model,
) -> tuple:
    diagnostic_result = run_diagnostic(diagnostic_responses)
    tier = diagnostic_result["tier"]
    misconception = diagnostic_result["misconception"]
    chunks = retrieve_chunks(user_query, tier, topic, collection, embed_model)
    chunks_text = format_chunks_for_prompt(chunks)
    prompt_messages = build_prompt(tier, misconception, chunks_text, user_query)
    sources = list({chunk["source"] for chunk in chunks})
    return tier, misconception, len(chunks), sources, prompt_messages


def run_session(
    user_query: str,
    diagnostic_responses: list,
    topic: str,
    collection: chromadb.Collection,
    embed_model: SentenceTransformer,
) -> dict:
    tier, misconception, n_chunks, sources, prompt_messages = _prepare_session(
        user_query, diagnostic_responses, topic, collection, embed_model
    )
    explanation = generate_explanation(prompt_messages)
    return {
        "tier": tier,
        "misconception": misconception,
        "chunks_retrieved": n_chunks,
        "explanation": explanation,
        "sources_used": sources,
    }


def run_session_stream(
    user_query: str,
    diagnostic_responses: list,
    topic: str,
    collection: chromadb.Collection,
    embed_model: SentenceTransformer,
):
    """Yields (tier, sources) once, then yields text chunks."""
    tier, misconception, n_chunks, sources, prompt_messages = _prepare_session(
        user_query, diagnostic_responses, topic, collection, embed_model
    )
    yield ("meta", tier, sources)
    for chunk in generate_explanation_stream(prompt_messages):
        yield ("chunk", chunk)
