# Adaptive Linear Algebra Explainer

A retrieval-augmented generation (RAG) system that diagnoses a student's linear algebra background and generates tier-calibrated explanations using Groq's Llama 3.3 70B.

## How It Works

1. **Diagnostic** — The system asks 3 questions to classify the student into one of three tiers:
   - Tier 1: Geometric Intuition — plain English, analogies, no notation
   - Tier 2: Formal Beginner — definitions paired with concrete examples
   - Tier 3: Algebraically Grounded — abstract formulation, formal proofs

2. **Retrieval** — The student's query is embedded and used to search a ChromaDB vector store, filtered by the diagnosed tier and selected topic.

3. **Generation** — Retrieved chunks are passed to Llama 3.3 70B (via Groq) with a tier-appropriate system prompt. Responses are streamed token-by-token and rendered with KaTeX for proper math display.

## Stack

| Component | Technology |
|---|---|
| Embedding | `sentence-transformers` (all-MiniLM-L6-v2) |
| Vector store | ChromaDB (local persistent) |
| Generation | Llama 3.3 70B via Groq API |
| Backend | FastAPI |
| Frontend | React + TypeScript + Vite |
| Evaluation | RAGAS faithfulness metric |

## Core Components

This project implements three of the course's core generative AI components:

- **RAG** — ChromaDB vector store with tier and topic metadata filtering
- **Prompt Engineering** — tier-specific system prompts with misconception correction
- **Synthetic Data Generation** — four knowledge base PDFs compiled from LaTeX source files authored for this project

## Setup

### Prerequisites

- Python 3.11+ (conda recommended)
- [Groq API key](https://console.groq.com) — free tier is sufficient
- Node.js 18+

### Backend

```bash
# Clone the repo
git clone https://github.com/muqeetmohd/adaptive-la-evaluator-explainer.git
cd adaptive-la-evaluator-explainer

# Create and activate environment
conda create -n la-explainer python=3.11 -y
conda activate la-explainer

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env
```

### Build the knowledge base

Run once to parse the synthetic PDFs, chunk them, embed with all-MiniLM-L6-v2, and store in ChromaDB:

```bash
python build_kb.py
```

> The `chroma_db/` directory is excluded from git due to size. Run `build_kb.py` to regenerate it — takes about 30 seconds.

Inspect the result:

```bash
python knowledge_base/inspect.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`.

### Start the API

In a separate terminal from the project root:

```bash
conda activate la-explainer
uvicorn api:app --host 0.0.0.0 --port 8000
```

## Running

1. Start the API server (port 8000)
2. Start the frontend dev server (port 5173)
3. Open `http://localhost:5173`
4. Answer the 3 diagnostic questions
5. Pick a topic from the list
6. Ask anything — responses stream in with math rendered via KaTeX

### Tests

```bash
# End-to-end pipeline smoke test
python tests/test_pipeline.py

# Retrieval unit test
python tests/test_retrieval.py
```

### Evaluation

```bash
python evaluation/run_eval.py
```

Outputs `evaluation/eval_results.csv` with RAGAS faithfulness scores per query, and `evaluation/flagged_outputs.csv` for outputs below 0.75.

## Project Structure

```
adaptive-la-evaluator-explainer/
├── data/raw/                  # Source PDFs (4 synthetic notes)
├── synthetic_sources/         # LaTeX source files for the PDFs
├── knowledge_base/
│   ├── parse.py               # PDF parsing + LaTeX equation preprocessing
│   ├── chunk.py               # Chunking + topic assignment
│   ├── embed.py               # Embedding + ChromaDB ingestion
│   ├── inspect.py             # KB quality inspection
│   └── topics.py              # Topic list
├── diagnostic/
│   └── diagnostic.py          # 3-question tier classifier
├── retrieval/
│   └── retrieve.py            # Tier + topic filtered vector search
├── generation/
│   ├── prompt.py              # Tier-specific prompt templates
│   └── generate.py            # Groq API call + streaming
├── evaluation/
│   ├── faithfulness.py        # RAGAS faithfulness scorer
│   ├── run_eval.py            # 30-query evaluation suite
│   └── rubrics/               # Manual tier calibration rubric
├── frontend/                  # React + TypeScript + Vite UI
├── tests/
│   ├── test_pipeline.py       # End-to-end smoke test
│   └── test_retrieval.py      # Retrieval unit test
├── api.py                     # FastAPI backend
├── pipeline.py                # Full pipeline orchestration
├── build_kb.py                # One-command KB builder
├── documentation.pdf          # Full project documentation
└── requirements.txt
```

## Knowledge Base

Four synthetic PDF sources authored for this project, each assigned a tier:

| File | Tier | Content |
|---|---|---|
| `vector_spaces_notes.pdf` | 1 | Plain-language intuition, analogies, no notation |
| `intro_linear_algebra_notes.pdf` | 2 | Definitions paired with concrete examples |
| `systems_row_reduction_notes.pdf` | 2 | Procedural treatment of systems, rank, determinants |
| `eigen_notes.pdf` | 3 | Abstract formulation, axioms, spectral theory |

15 topics covered: vectors, matrix multiplication, linear transformations, determinants, eigenvalues, eigenvectors, vector spaces, linear independence, basis, rank, dot product, orthogonality, systems of equations, row reduction, matrix inverse.

## Example Outputs

See [`example_outputs/`](example_outputs/) for sample responses showing the same question answered across all three tiers.
