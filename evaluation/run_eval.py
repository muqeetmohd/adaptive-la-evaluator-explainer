import csv
import os
from sentence_transformers import SentenceTransformer

from knowledge_base.embed import load_knowledge_base
from pipeline import run_session
from evaluation.faithfulness import score_faithfulness

_EMBED_MODEL = "all-MiniLM-L6-v2"
_OUTPUT_CSV = "evaluation/eval_results.csv"
_FLAGGED_CSV = "evaluation/flagged_outputs.csv"

_TIER_RESPONSES = {
    1: ["true", "multiply rows and columns", "no"],
    2: ["false", "it transforms the vector", "yes, set of vectors with addition"],
    3: [
        "false because transformations dont commute",
        "it applies a linear transformation",
        "yes, defined by axioms abstractly",
    ],
}

_TEST_SET = [
    # Tier 1
    {"query": "What is a vector?", "tier": 1, "topic": "vectors"},
    {"query": "What does a matrix do?", "tier": 1, "topic": "matrix_multiplication"},
    {"query": "How do you add two vectors?", "tier": 1, "topic": "vectors"},
    {"query": "What is a dot product?", "tier": 1, "topic": "dot_product"},
    {"query": "What does row reduction mean?", "tier": 1, "topic": "row_reduction"},
    {"query": "How do you solve a system of equations?", "tier": 1, "topic": "systems_of_equations"},
    {"query": "What is the rank of a matrix?", "tier": 1, "topic": "rank"},
    {"query": "What does it mean for vectors to be independent?", "tier": 1, "topic": "linear_independence"},
    {"query": "What is a basis?", "tier": 1, "topic": "basis"},
    {"query": "What is a determinant?", "tier": 1, "topic": "determinants"},
    # Tier 2
    {"query": "Why is matrix multiplication not commutative?", "tier": 2, "topic": "matrix_multiplication"},
    {"query": "What is a linear transformation?", "tier": 2, "topic": "linear_transformations"},
    {"query": "What does the determinant tell you geometrically?", "tier": 2, "topic": "determinants"},
    {"query": "What is orthogonality?", "tier": 2, "topic": "orthogonality"},
    {"query": "How does Gaussian elimination work?", "tier": 2, "topic": "row_reduction"},
    {"query": "What is the relationship between rank and solutions?", "tier": 2, "topic": "rank"},
    {"query": "What is a vector space?", "tier": 2, "topic": "vector_spaces"},
    {"query": "How do you find the inverse of a matrix?", "tier": 2, "topic": "matrix_inverse"},
    {"query": "What does a basis represent?", "tier": 2, "topic": "basis"},
    {"query": "What is an eigenvector?", "tier": 2, "topic": "eigenvectors"},
    # Tier 3
    {"query": "What is the relationship between eigenvalues and the characteristic polynomial?", "tier": 3, "topic": "eigenvalues"},
    {"query": "How do eigenvalues relate to linear transformations structurally?", "tier": 3, "topic": "eigenvectors"},
    {"query": "What are the axioms that define a vector space?", "tier": 3, "topic": "vector_spaces"},
    {"query": "What is the null space and how does it relate to linear independence?", "tier": 3, "topic": "linear_independence"},
    {"query": "Why does a non-zero determinant guarantee invertibility?", "tier": 3, "topic": "determinants"},
    {"query": "What is the spectral theorem?", "tier": 3, "topic": "eigenvalues"},
    {"query": "How does orthogonal projection work in inner product spaces?", "tier": 3, "topic": "orthogonality"},
    {"query": "What is the rank-nullity theorem?", "tier": 3, "topic": "rank"},
    {"query": "How is the matrix inverse related to linear maps?", "tier": 3, "topic": "matrix_inverse"},
    {"query": "What makes a set of vectors a basis for a subspace?", "tier": 3, "topic": "basis"},
]


def run_evaluation():
    collection = load_knowledge_base()
    embed_model = SentenceTransformer(_EMBED_MODEL)

    results = []
    flagged = []

    for i, case in enumerate(_TEST_SET):
        print(f"[{i+1}/{len(_TEST_SET)}] Tier {case['tier']}: {case['query']}")
        try:
            session = run_session(
                user_query=case["query"],
                diagnostic_responses=_TIER_RESPONSES[case["tier"]],
                topic=case["topic"],
                collection=collection,
                embed_model=embed_model,
            )
            contexts = []
            from retrieval.retrieve import retrieve_chunks
            chunks = retrieve_chunks(
                case["query"], case["tier"], case["topic"], collection, embed_model
            )
            contexts = [c["text"] for c in chunks]

            faith_score = score_faithfulness(
                question=case["query"],
                answer=session["explanation"],
                contexts=contexts,
            )

            row = {
                "query": case["query"],
                "tier": case["tier"],
                "faithfulness_score": faith_score,
                "explanation": session["explanation"],
                "sources": ", ".join(session["sources_used"]),
            }
            results.append(row)

            if faith_score < 0.75:
                flagged.append(row)

        except Exception as e:
            print(f"  ERROR: {e}")

    _write_csv(results, _OUTPUT_CSV)
    _write_csv(flagged, _FLAGGED_CSV)
    _print_summary(results, flagged)


def _write_csv(rows: list, path: str):
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {path}")


def _print_summary(results: list, flagged: list):
    if not results:
        print("No results to summarize.")
        return

    scores = [r["faithfulness_score"] for r in results]
    print(f"\n=== Evaluation Summary ===")
    print(f"Overall mean faithfulness: {sum(scores)/len(scores):.3f}")

    for tier in [1, 2, 3]:
        tier_scores = [r["faithfulness_score"] for r in results if r["tier"] == tier]
        if tier_scores:
            print(f"Tier {tier} mean faithfulness: {sum(tier_scores)/len(tier_scores):.3f}")

    print(f"Outputs flagged for review (score < 0.75): {len(flagged)}")
    print(f"Results saved to: {_OUTPUT_CSV}")
    print(f"Flagged outputs saved to: {_FLAGGED_CSV}")


if __name__ == "__main__":
    run_evaluation()
