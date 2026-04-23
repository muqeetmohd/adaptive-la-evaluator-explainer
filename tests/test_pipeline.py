from knowledge_base.embed import load_knowledge_base
from sentence_transformers import SentenceTransformer
from pipeline import run_session

_EMBED_MODEL = "all-MiniLM-L6-v2"

_TEST_CASES = [
    {
        "label": "Tier 1",
        "responses": ["true", "multiply rows and columns", "no"],
        "expected_tier": 1,
    },
    {
        "label": "Tier 2",
        "responses": [
            "false",
            "it transforms the vector",
            "yes, set of vectors with addition",
        ],
        "expected_tier": 2,
    },
    {
        "label": "Tier 3",
        "responses": [
            "false because transformations dont commute",
            "it applies a linear transformation",
            "yes, defined by axioms abstractly",
        ],
        "expected_tier": 3,
    },
]


def test_pipeline():
    collection = load_knowledge_base()
    model = SentenceTransformer(_EMBED_MODEL)

    for case in _TEST_CASES:
        print(f"\n=== {case['label']} test ===")
        result = run_session(
            user_query="What is an eigenvector?",
            diagnostic_responses=case["responses"],
            topic="eigenvectors",
            collection=collection,
            embed_model=model,
        )
        print(result)

        assert result["tier"] == case["expected_tier"], (
            f"Expected tier {case['expected_tier']}, got {result['tier']}"
        )
        assert isinstance(result["explanation"], str) and len(result["explanation"]) > 0
        assert result["chunks_retrieved"] > 0

    print("\nAll pipeline tests passed.")


if __name__ == "__main__":
    test_pipeline()
