import re
from langchain_community.document_loaders import PyMuPDFLoader

_EQUATION_PATTERNS = [
    (r"\\begin\{equation\}.*?\\end\{equation\}", re.DOTALL),
    (r"\$\$.*?\$\$", re.DOTALL),
    (r"\$[^$\n]+?\$", 0),
]


def _preprocess(text: str) -> str:
    for pattern, flags in _EQUATION_PATTERNS:
        text = re.sub(pattern, "[math expression]", text, flags=flags)
    return text


def parse_pdf(pdf_path: str, source_name: str) -> list:
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()
    return [_preprocess(doc.page_content) for doc in docs]


def parse_all_sources() -> dict:
    sources = {
        "intro_linear_algebra_notes": "data/raw/intro_linear_algebra_notes.pdf",
        "systems_row_reduction_notes": "data/raw/systems_row_reduction_notes.pdf",
        "vector_spaces_notes": "data/raw/vector_spaces_notes.pdf",
        "eigen_notes": "data/raw/eigen_notes.pdf",
    }
    return {name: parse_pdf(path, name) for name, path in sources.items()}
