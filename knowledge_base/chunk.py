from langchain_text_splitters import RecursiveCharacterTextSplitter

_TIER_MAP = {
    "intro_linear_algebra_notes": 2,
    "systems_row_reduction_notes": 2,
    "vector_spaces_notes": 1,
    "eigen_notes": 3,
}

_KEYWORD_TOPIC_MAP = [
    ("eigenvector", "eigenvectors"),
    ("eigenvalue", "eigenvalues"),
    ("linear transform", "linear_transformations"),
    ("matrix multipli", "matrix_multiplication"),
    ("vector space", "vector_spaces"),
    ("linear independen", "linear_independence"),
    ("system of equation", "systems_of_equations"),
    ("basis", "basis"),
    ("determinant", "determinants"),
    ("dot product", "dot_product"),
    ("orthogon", "orthogonality"),
    ("row reduction", "row_reduction"),
    ("gauss", "row_reduction"),
    ("rank", "rank"),
    ("inverse", "matrix_inverse"),
    ("vector", "vectors"),
]


def chunk_source(pages: list, source_name: str) -> list:
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=75)
    full_text = "\n".join(pages)
    chunks = splitter.split_text(full_text)
    return [
        {
            "text": chunk,
            "source": source_name,
            "tier": _TIER_MAP.get(source_name, 2),
            "topic": "unassigned",
        }
        for chunk in chunks
    ]


def chunk_all_sources(parsed: dict) -> list:
    result = []
    for source_name, pages in parsed.items():
        result.extend(chunk_source(pages, source_name))
    return result


def assign_topics(chunks: list) -> list:
    for chunk in chunks:
        text_lower = chunk["text"].lower()
        assigned = "vectors"
        for keyword, topic in _KEYWORD_TOPIC_MAP:
            if keyword in text_lower:
                assigned = topic
                break
        chunk["topic"] = assigned
    return chunks
