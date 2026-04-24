# Adaptive Linear Algebra Explainer

A retrieval-augmented generation (RAG) system that diagnoses a student's linear algebra background and generates tier-calibrated explanations using a local LLM.

## How It Works

1. **Diagnostic** — The system asks 3 questions to classify the student into one of three tiers:
   - Tier 1: Geometric intuition (beginner)
   - Tier 2: Formal beginner (operational understanding)
   - Tier 3: Algebraically grounded (abstract/axiomatic)

2. **Retrieval** — The student's query is embedded and used to search a ChromaDB vector store, filtered by the diagnosed tier and selected topic.

3. **Generation** — Retrieved chunks are passed to Mistral 7B Instruct (via Ollama) with a tier-appropriate system prompt. The model is grounded to only use the retrieved context.

## Stack

| Component | Technology |
|---|---|
| Embedding | `sentence-transformers` (all-MiniLM-L6-v2) |
| Vector store | ChromaDB (local persistent) |
| Generation | Mistral 7B Instruct via Ollama |
| Interface | Gradio |
| Evaluation | RAGAS faithfulness metric |

## Setup

### Prerequisites

- Python 3.12
- [Ollama](https://ollama.com) installed and running

### Install

```bash
# Clone and enter the project
cd adaptive-la-evaluator-explainer

# Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Pull the model

```bash
ollama pull mistral:instruct
```

### Build the knowledge base

Run once to parse the source PDFs, chunk them, embed with all-MiniLM-L6-v2, and store in ChromaDB:

```bash
python build_kb.py
```

Inspect the result:

```bash
python knowledge_base/inspect.py
```

## Running

### Launch the UI

```bash
python interface/app.py
```

Opens at `http://127.0.0.1:7860`. Answer the 3 diagnostic questions, select a topic from the dropdown, then ask anything about it.

### Smoke test (requires Ollama running)

```bash
python tests/test_pipeline.py
```

Runs the full pipeline for all 3 tiers and asserts correctness.

### Retrieval test

```bash
python tests/test_retrieval.py
```

## Project Structure

```
adaptive-la-evaluator-explainer/
├── data/raw/                  # Source PDFs (4 synthetic notes, tiered by level)
├── synthetic_sources/         # LaTeX source files for the PDFs
├── knowledge_base/
│   ├── parse.py               # PDF parsing + LaTeX equation preprocessing
│   ├── chunk.py               # Chunking + topic assignment
│   ├── embed.py               # Embedding + ChromaDB ingestion
│   ├── inspect.py             # KB quality inspection
│   └── topics.py              # Topic list + prerequisite graph
├── diagnostic/
│   └── diagnostic.py          # 3-question tier classifier
├── retrieval/
│   └── retrieve.py            # Tier + topic filtered vector search
├── generation/
│   ├── prompt.py              # Tier-specific prompt templates
│   └── generate.py            # Ollama API call
├── evaluation/
│   ├── faithfulness.py        # RAGAS faithfulness scorer
│   ├── run_eval.py            # 30-query evaluation suite
│   └── rubrics/               # Manual tier calibration rubric
├── interface/
│   └── app.py                 # Gradio UI
├── tests/
│   ├── test_pipeline.py       # End-to-end smoke test
│   └── test_retrieval.py      # Retrieval unit test
├── pipeline.py                # Full pipeline orchestration
├── build_kb.py                # One-command KB builder
├── verify_ollama.py           # Ollama connection check
└── requirements.txt
```

## Knowledge Base

Four synthetic PDF sources, each assigned a tier:

| File | Tier | Content |
|---|---|---|
| `vector_spaces_notes.pdf` | 1 | Plain-language intuition, analogies, no notation |
| `intro_linear_algebra_notes.pdf` | 2 | Definitions paired with concrete examples |
| `systems_row_reduction_notes.pdf` | 2 | Procedural treatment of systems, rank, determinants |
| `eigen_notes.pdf` | 3 | Abstract formulation, axioms, spectral theory |

All 15 core topics are covered: vectors, matrix multiplication, linear transformations, determinants, eigenvalues, eigenvectors, vector spaces, linear independence, basis, rank, dot product, orthogonality, systems of equations, row reduction, matrix inverse.

## Evaluation

Run the full 30-query RAGAS evaluation suite:

```bash
python evaluation/run_eval.py
```

Outputs `evaluation/eval_results.csv` with faithfulness scores per query, and `evaluation/flagged_outputs.csv` for outputs scoring below 0.75.
