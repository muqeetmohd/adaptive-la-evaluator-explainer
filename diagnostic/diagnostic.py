QUESTIONS = [
    "True or false: for any two matrices A and B, AB = BA.",
    "In your own words, what does multiplying a vector by a matrix actually do?",
    (
        "Have you encountered the concept of a vector space before? "
        "If yes, how would you describe it?"
    ),
]

_Q1_EXPLANATION_KEYWORDS = {"why", "because", "transform", "example", "counter"}
_Q2_ARITHMETIC_KEYWORDS = {"row", "column", "multiply", "arithmetic", "number"}
_Q2_TRANSFORM_KEYWORDS = {"transform", "move", "change"}
_Q2_SPACE_KEYWORDS = {"space", "stretch", "rotate", "linear transformation"}
_Q3_PROCEDURAL_KEYWORDS = {"addition", "scalar", "multiplication", "set of vectors"}
_Q3_ABSTRACT_KEYWORDS = {"axiom", "abstract", "beyond", "field", "subspace"}


def _contains_any(text: str, keywords: set) -> bool:
    return any(kw in text for kw in keywords)


def classify_response(question_index: int, response: str) -> int:
    r = response.lower()

    if question_index == 0:
        if "true" in r:
            return 1
        if "false" in r and not _contains_any(r, _Q1_EXPLANATION_KEYWORDS):
            return 2
        if "false" in r and _contains_any(r, _Q1_EXPLANATION_KEYWORDS):
            return 3
        return 2

    if question_index == 1:
        has_space = _contains_any(r, _Q2_SPACE_KEYWORDS)
        has_transform = _contains_any(r, _Q2_TRANSFORM_KEYWORDS)
        has_arithmetic = _contains_any(r, _Q2_ARITHMETIC_KEYWORDS)
        if has_space:
            return 3
        if has_transform:
            return 2
        if has_arithmetic:
            return 1
        return 2

    if question_index == 2:
        has_yes = "yes" in r
        if not has_yes or "no" in r or "list" in r or "numbers" in r:
            return 1
        if has_yes and _contains_any(r, _Q3_ABSTRACT_KEYWORDS):
            return 3
        if has_yes and _contains_any(r, _Q3_PROCEDURAL_KEYWORDS):
            return 2
        if has_yes:
            return 2
        return 1

    return 2


def run_diagnostic(responses: list) -> dict:
    tier_scores = [classify_response(i, r) for i, r in enumerate(responses)]

    counts = {1: tier_scores.count(1), 2: tier_scores.count(2), 3: tier_scores.count(3)}
    modal_tier = min(counts, key=lambda t: (-counts[t], t))

    misconceptions = []
    if tier_scores[0] == 1:
        misconceptions.append(
            "Student believes matrix multiplication is commutative (AB = BA for all matrices)"
        )
    if tier_scores[1] == 1:
        misconceptions.append(
            "Student views matrix-vector multiplication as purely arithmetic "
            "rather than a geometric transformation"
        )

    return {
        "tier": modal_tier,
        "tier_scores": tier_scores,
        "misconception": " | ".join(misconceptions) if misconceptions else None,
    }
