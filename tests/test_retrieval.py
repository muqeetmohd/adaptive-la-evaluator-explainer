from knowledge_base.embed import load_knowledge_base
from sentence_transformers import SentenceTransformer
from retrieval.retrieve import retrieve_chunks, format_chunks_for_prompt

_EMBED_MODEL = "all-MiniLM-L6-v2"


def test_retrieval():
    collection = load_knowledge_base()
    model = SentenceTransformer(_EMBED_MODEL)

    for tier in [1, 2, 3]:
        print(f"\n--- Tier {tier} retrieval ---")
        chunks = retrieve_chunks(
            query="What is an eigenvector?",
            tier=tier,
            topic="eigenvectors",
            collection=collection,
            model=model,
        )
        assert len(chunks) > 0, f"No chunks returned for tier {tier}"
        print(f"Retrieved {len(chunks)} chunks")
        print(format_chunks_for_prompt(chunks[:2]))

    print("\nAll retrieval tests passed.")


if __name__ == "__main__":
    test_retrieval()
