# Development Steps — Adaptive Linear Algebra Explainer
### Ordered build sequence for VS Code Copilot

---

## Context to paste at the start of every Copilot session

```
I am building an adaptive linear algebra explainer using RAG.
The system diagnoses a student's level via 3 questions, classifies them into
Tier 1 (geometric intuition), Tier 2 (formal beginner), or Tier 3 (algebraically grounded),
then retrieves explanation chunks from a ChromaDB vector database filtered by tier and topic,
and generates a grounded explanation using Mistral 7B Instruct via Ollama.

Stack:
- Python 3.11+
- LangChain (document loading + chunking only)
- Sentence Transformers: all-MiniLM-L6-v2 (embedding)
- ChromaDB (local persistent vector store)
- Ollama serving Mistral 7B Instruct (generation)
- Gradio (interface)
- RAGAS (faithfulness evaluation, configured for local Mistral)

Do not use LangChain for retrieval or generation — those are custom.
Do not suggest OpenAI API — everything runs locally.
```

Paste this block at the top of each new Copilot chat before giving it a task.

---

## Phase 1 — Project Setup

### Step 1.1 — Initialize project structure
```
Create the following folder structure:

adaptive-explainer/
├── data/
│   ├── raw/          # PDF source files go here
│   └── processed/    # Cleaned text after parsing
├── knowledge_base/
│   ├── parse.py      # Document parsing + equation preprocessing
│   ├── chunk.py      # Chunking logic
│   ├── embed.py      # Embedding + ChromaDB ingestion
│   └── topics.py     # Topic list + prerequisite lookup table
├── diagnostic/
│   └── diagnostic.py # Q1/Q2/Q3 + rule-based tier routing
├── retrieval/
│   └── retrieve.py   # Custom ChromaDB query with metadata filtering
├── generation/
│   ├── prompt.py     # Prompt template builder
│   └── generate.py   # Ollama API call
├── evaluation/
│   ├── faithfulness.py  # RAGAS faithfulness scorer
│   └── rubrics/         # Manual scoring sheets (markdown)
├── interface/
│   └── app.py        # Gradio app
├── tests/
│   └── test_retrieval.py
├── requirements.txt
└── README.md
```

### Step 1.2 — Install dependencies
```
Create requirements.txt with the following:

langchain
langchain-community
pymupdf
sentence-transformers
chromadb
ollama
gradio
ragas
datasets
pandas
python-dotenv

Then run: pip install -r requirements.txt
```

### Step 1.3 — Verify Ollama is running with Mistral
```
Write a script verify_ollama.py that:
1. Sends a test prompt to http://localhost:11434/api/chat
   using the model "mistral:instruct"
2. Prints the response
3. Prints "Ollama connection verified" if successful
4. Raises a clear error message if connection fails

Use the requests library, not the ollama Python package.
```

---

## Phase 2 — Knowledge Base Build

### Step 2.1 — Define topic list and prerequisite lookup table
```
In knowledge_base/topics.py, define:

1. TOPIC_LIST: a list of 15 topic strings:
   "vectors", "matrix_multiplication", "linear_transformations",
   "determinants", "eigenvalues", "eigenvectors", "vector_spaces",
   "linear_independence", "basis", "rank", "dot_product",
   "orthogonality", "systems_of_equations", "row_reduction", "matrix_inverse"

2. PREREQUISITES: a dict mapping each topic to a list of prerequisite topics:
   {
     "eigenvalues": ["linear_transformations", "determinants"],
     "eigenvectors": ["eigenvalues", "linear_transformations"],
     "linear_transformations": ["matrix_multiplication", "vectors"],
     "matrix_multiplication": ["vectors"],
     "vector_spaces": ["vectors", "linear_independence"],
     "linear_independence": ["vectors", "basis"],
     "basis": ["linear_independence", "vector_spaces"],
     "rank": ["row_reduction", "linear_independence"],
     "orthogonality": ["dot_product", "vector_spaces"],
     "determinants": ["matrix_multiplication", "row_reduction"],
     "row_reduction": ["systems_of_equations"],
     "matrix_inverse": ["matrix_multiplication", "determinants"],
     "dot_product": ["vectors"],
     "systems_of_equations": ["vectors"],
     "vectors": []
   }

3. get_prerequisites(topic: str) -> list[str]:
   returns the prerequisite list for a given topic,
   returns empty list if topic not found
```

### Step 2.2 — Document parsing pipeline
```
In knowledge_base/parse.py, write a function:

parse_pdf(pdf_path: str, source_name: str) -> list[str]

That:
1. Uses LangChain's PyMuPDFLoader to load the PDF
2. Extracts raw text from each page
3. Runs a preprocessing step that replaces LaTeX equation blocks
   (patterns like \begin{equation}...\end{equation} and $$...$$
   and inline $...$ math) with a plain-language placeholder:
   "[math expression]"
4. Returns a list of cleaned page strings

Also write:
parse_all_sources() -> dict
That calls parse_pdf for each of the 4 sources and returns:
{
  "mit_ocw": [...],
  "openstax": [...],
  "pauls_notes": [...],
  "axler": [...]
}

PDF files are in data/raw/ named:
mit_ocw.pdf, openstax.pdf, pauls_notes.pdf, axler.pdf
```

### Step 2.3 — Chunking pipeline
```
In knowledge_base/chunk.py, write a function:

chunk_source(pages: list[str], source_name: str) -> list[dict]

That:
1. Joins the page strings into a single text
2. Uses LangChain's RecursiveCharacterTextSplitter with:
   chunk_size=400, chunk_overlap=75
3. For each chunk, creates a dict:
   {
     "text": <chunk text>,
     "source": <source_name>,
     "tier": <int — assigned by source using this mapping:
               "mit_ocw" -> 2,
               "openstax" -> 2,
               "pauls_notes" -> 1,
               "axler" -> 3>,
     "topic": "unassigned"   # placeholder — assigned in Step 2.4
   }
4. Returns the list of chunk dicts

Also write:
chunk_all_sources(parsed: dict) -> list[dict]
That calls chunk_source for all 4 sources and returns a flat list.
```

### Step 2.4 — Topic assignment
```
In knowledge_base/chunk.py, add a function:

assign_topics(chunks: list[dict]) -> list[dict]

That uses keyword matching to assign a topic from TOPIC_LIST to each chunk.
For each chunk:
1. Lowercase the chunk text
2. Check for keyword presence using this mapping:
   {
     "eigenvector": "eigenvectors",
     "eigenvalue": "eigenvalues",
     "linear transform": "linear_transformations",
     "matrix multipli": "matrix_multiplication",
     "vector space": "vector_spaces",
     "linear independen": "linear_independence",
     "basis": "basis",
     "determinant": "determinants",
     "dot product": "dot_product",
     "orthogon": "orthogonality",
     "row reduction": "row_reduction",
     "gauss": "row_reduction",
     "rank": "rank",
     "inverse": "matrix_inverse",
     "system of equation": "systems_of_equations",
     "vector": "vectors"
   }
3. Assign the first matching topic (in the order above — more specific first)
4. If no match, assign topic = "vectors" as default
5. Return the updated chunk list

Note: order matters — check more specific terms before general ones
(e.g. "eigenvector" before "vector")
```

### Step 2.5 — Embedding and ChromaDB ingestion
```
In knowledge_base/embed.py, write:

build_knowledge_base(chunks: list[dict], persist_dir: str = "./chroma_db")

That:
1. Initializes a persistent ChromaDB client at persist_dir
2. Creates or gets a collection named "linear_algebra"
3. Loads the Sentence Transformers model "all-MiniLM-L6-v2"
4. For each chunk:
   a. Generates an embedding using model.encode(chunk["text"])
   b. Creates a unique ID: f"{chunk['source']}_{index}"
   c. Adds to ChromaDB with:
      - document: chunk["text"]
      - embedding: embedding vector
      - metadata: {tier, source, topic}
5. Prints progress every 100 chunks
6. Prints total chunks ingested on completion

Also write:
load_knowledge_base(persist_dir: str = "./chroma_db") -> chromadb.Collection
That loads and returns the existing collection without rebuilding.
```

### Step 2.6 — Spot-check script
```
Write a script knowledge_base/inspect.py that:
1. Loads the ChromaDB collection
2. Prints total chunk count
3. Prints chunk count broken down by tier (1, 2, 3)
4. Prints chunk count broken down by source
5. Prints chunk count broken down by topic
6. Retrieves and prints 3 random chunks from each tier
   so you can manually verify chunk quality

Run this after building the knowledge base to verify
ingestion worked correctly before moving to retrieval.
```

---

## Phase 3 — Diagnostic Module

### Step 3.1 — Diagnostic questions and routing logic
```
In diagnostic/diagnostic.py, implement:

QUESTIONS: list of 3 question strings:
  Q1: "True or false: for any two matrices A and B, AB = BA."
  Q2: "In your own words, what does multiplying a vector by a matrix actually do?"
  Q3: "Have you encountered the concept of a vector space before?
       If yes, how would you describe it?"

classify_response(question_index: int, response: str) -> int
  Classifies a single response as tier 1, 2, or 3.
  question_index is 0, 1, or 2 (for Q1, Q2, Q3).

  Rules:
  Q1 (index 0):
    - response contains "true" (case insensitive) -> 1
    - response contains "false" but not explanation keywords
      ("why", "because", "transform", "example", "counter") -> 2
    - response contains "false" AND explanation keywords -> 3

  Q2 (index 1):
    - response contains arithmetic keywords
      ("row", "column", "multiply", "arithmetic", "number") but
      NOT transformation keywords -> 1
    - response contains transformation keywords
      ("transform", "move", "change") but NOT space keywords -> 2
    - response contains space keywords
      ("space", "stretch", "rotate", "linear transformation") -> 3

  Q3 (index 2):
    - response contains "no" or "list" or "numbers" -> 1
    - response contains "yes" AND procedural keywords
      ("addition", "scalar", "multiplication", "set of vectors") -> 2
    - response contains "yes" AND abstract keywords
      ("axiom", "abstract", "beyond", "field", "subspace") -> 3
    - default if "yes" but no clear keywords -> 2

run_diagnostic(responses: list[str]) -> dict
  Takes a list of 3 response strings.
  Returns:
  {
    "tier": <modal tier — ties go to lower tier>,
    "tier_scores": [t1, t2, t3],   # per-question tier classifications
    "misconception": <string describing identified misconception or None>
  }

  Misconception rules:
  - If Q1 classified as Tier 1: "Student believes matrix multiplication
    is commutative (AB = BA for all matrices)"
  - If Q2 classified as Tier 1: "Student views matrix-vector multiplication
    as purely arithmetic rather than a geometric transformation"
  - If both above: combine both misconception strings
  - Otherwise: None
```

---

## Phase 4 — Retrieval Module

### Step 4.1 — Custom retrieval function
```
In retrieval/retrieve.py, implement:

retrieve_chunks(
    query: str,
    tier: int,
    topic: str,
    collection: chromadb.Collection,
    model: SentenceTransformer,
    top_k: int = 5
) -> list[dict]

That:
1. Embeds the query using model.encode(query)
2. Queries ChromaDB with:
   - embedding: query embedding
   - n_results: top_k
   - where filter: {"$and": [{"tier": tier}, {"topic": topic}]}
3. If results < 3, runs a fallback query with only tier filter:
   - where filter: {"tier": tier}
4. Returns list of dicts:
   [{"text": ..., "source": ..., "tier": ..., "topic": ...}, ...]

Also implement:
format_chunks_for_prompt(chunks: list[dict]) -> str
  Formats retrieved chunks as a numbered list with source attribution:
  "
  [1] (Source: mit_ocw, Topic: eigenvectors)
  <chunk text>

  [2] (Source: axler, Topic: eigenvectors)
  <chunk text>
  ...
  "
```

---

## Phase 5 — Generation Module

### Step 5.1 — Prompt template builder
```
In generation/prompt.py, implement:

TIER_DESCRIPTIONS = {
    1: "a beginner who needs plain English and physical intuition — use no formal notation, explain using analogies and real-world examples",
    2: "an intermediate learner who understands operations but needs conceptual framing — pair every definition with a concrete example",
    3: "an advanced student comfortable with abstract mathematical structures — use precise mathematical language and formal definitions"
}

build_prompt(
    tier: int,
    misconception: str | None,
    chunks_text: str,
    user_query: str
) -> dict

Returns an Ollama-compatible messages dict:
{
  "messages": [
    {
      "role": "system",
      "content": <system prompt using tier description,
                  grounding constraint, misconception if present,
                  attribution instruction>
    },
    {
      "role": "user",
      "content": f"Please explain: {user_query}\n\nRetrieved context:\n{chunks_text}"
    }
  ]
}

System prompt template:
"You are explaining a linear algebra concept to {tier_description}.

IMPORTANT RULES:
1. Use ONLY the information in the retrieved context provided by the user.
   Do not add any information from outside the retrieved passages.
2. {misconception_instruction}
3. End your explanation by citing which source(s) you drew from,
   using the source labels provided in the context.

Respond with a clear, structured explanation."

misconception_instruction:
- If misconception is not None:
  f"The student currently holds this misconception — address it directly
    and correct it in your explanation: {misconception}"
- If None:
  "Address any common misconceptions relevant to this topic."
```

### Step 5.2 — Generation call
```
In generation/generate.py, implement:

generate_explanation(
    prompt_messages: dict,
    model: str = "mistral:instruct",
    ollama_url: str = "http://localhost:11434/api/chat"
) -> str

That:
1. Sends a POST request to ollama_url with:
   {
     "model": model,
     "messages": prompt_messages["messages"],
     "stream": False
   }
2. Returns the response content string
3. Raises a clear error if Ollama is not reachable
4. Raises a clear error if response is malformed
```

---

## Phase 6 — Full Pipeline Integration

### Step 6.1 — End-to-end pipeline function
```
In a new file pipeline.py, implement:

run_session(
    user_query: str,
    diagnostic_responses: list[str],
    topic: str,
    collection: chromadb.Collection,
    embed_model: SentenceTransformer
) -> dict

That runs the full pipeline in sequence:
1. run_diagnostic(diagnostic_responses)
   -> get tier, misconception
2. retrieve_chunks(user_query, tier, topic, collection, embed_model)
   -> get chunks
3. format_chunks_for_prompt(chunks)
   -> get chunks_text
4. build_prompt(tier, misconception, chunks_text, user_query)
   -> get prompt_messages
5. generate_explanation(prompt_messages)
   -> get explanation

Returns:
{
  "tier": tier,
  "misconception": misconception,
  "chunks_retrieved": len(chunks),
  "explanation": explanation,
  "sources_used": list of unique sources from retrieved chunks
}
```

### Step 6.2 — Integration test
```
In tests/test_pipeline.py, write a test that:
1. Loads the ChromaDB collection
2. Loads the embedding model
3. Runs run_session() with:
   - user_query: "What is an eigenvector?"
   - diagnostic_responses:
       Tier 1 test: ["true", "multiply rows and columns", "no"]
       Tier 2 test: ["false", "it transforms the vector", "yes, set of vectors with addition"]
       Tier 3 test: ["false because transformations dont commute", "it applies a linear transformation", "yes, defined by axioms abstractly"]
   - topic: "eigenvectors"
4. Prints the full output dict for each test case
5. Asserts:
   - tier is 1, 2, 3 respectively
   - explanation is non-empty string
   - chunks_retrieved > 0

This is your smoke test — run it after Step 6.1 before building the interface.
```

---

## Phase 7 — Gradio Interface

### Step 7.1 — Gradio app
```
In interface/app.py, build a Gradio Blocks app with this flow:

STATE: store diagnostic_responses list and current_question_index

LAYOUT:
- Title: "Adaptive Linear Algebra Explainer"
- Subtitle: "Answer 3 quick questions so I can explain at your level."
- Chat window (gr.Chatbot)
- Text input + Submit button
- Topic dropdown: list of 15 topics from TOPIC_LIST

FLOW:
Stage 1 — Diagnostic (questions 0, 1, 2):
  On each submit:
  - Append user response to diagnostic_responses
  - Display next question in chat
  - After 3 responses, move to Stage 2

Stage 2 — Query:
  - Display: "Thanks! Now ask me anything about {selected_topic}."
  - On submit: run run_session() with collected responses + query + topic
  - Display explanation in chat
  - Display tier classification and sources used below chat

IMPORTANT:
- Load ChromaDB collection and embedding model ONCE at startup,
  not on each request
- Show a spinner while generating
- Handle Ollama connection errors gracefully with a user-facing message
```

---

## Phase 8 — Evaluation

### Step 8.1 — Configure RAGAS with local Mistral
```
In evaluation/faithfulness.py, implement:

setup_ragas_with_local_mistral() -> object
  Configures RAGAS to use Mistral via Ollama as the judge LLM.
  Uses langchain_community.llms.Ollama with model="mistral:instruct"
  as the LLM and all-MiniLM-L6-v2 as the embedding model.
  Returns configured ragas evaluator.

score_faithfulness(
    question: str,
    answer: str,
    contexts: list[str]
) -> float
  Runs RAGAS faithfulness metric on a single output.
  Returns score between 0 and 1.
  Prints a warning if score < 0.75.
```

### Step 8.2 — Evaluation runner
```
In evaluation/run_eval.py, write a script that:

1. Defines a test set of 30 queries — 10 per tier:
   Tier 1 queries: basic concept questions
     (e.g. "What is a vector?", "What does a matrix do?", ...)
   Tier 2 queries: operational questions
     (e.g. "Why is matrix multiplication not commutative?", ...)
   Tier 3 queries: structural questions
     (e.g. "What is the relationship between eigenvalues and
             the characteristic polynomial?", ...)

2. For each query:
   a. Run run_session() with appropriate diagnostic responses for that tier
   b. Score faithfulness via score_faithfulness()
   c. Save result to a CSV: query, tier, faithfulness_score, explanation, sources

3. Prints summary statistics:
   - Mean faithfulness score overall and per tier
   - Number of outputs scoring below 0.75 (flag for manual review)

4. Saves flagged outputs to evaluation/flagged_outputs.csv
   for manual tier calibration review
```

### Step 8.3 — Manual rubric files
```
Create evaluation/rubrics/tier_calibration_rubric.md with:

A scoring rubric (1-3 scale) for human reviewers to assess
whether an explanation's vocabulary and framing match the diagnosed tier:

Score 1 — Clearly miscalibrated:
  - Tier 1 output contains formal notation or abstract definitions
    with no plain-language explanation
  - Tier 3 output uses only analogies with no formal mathematical language

Score 2 — Partially calibrated:
  - Mostly appropriate but contains occasional vocabulary mismatches
  - Examples are present but not well-matched to tier level

Score 3 — Well-calibrated:
  - Vocabulary, notation level, and examples are consistently
    appropriate for the diagnosed tier
  - A student at that tier could follow the explanation without
    needing outside knowledge

Include 1 example of each score level for each tier (9 examples total).
```

---

## Build Order Summary

```
Week 4-5:  Steps 1.1 → 1.2 → 1.3 → 2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6
Week 6:    Steps 3.1 → 4.1
Week 7:    Steps 5.1 → 5.2 → 6.1 → 6.2 (smoke test)
Week 8:    Step 7.1 (Gradio interface)
Week 9-10: Steps 8.1 → 8.2 → 8.3 (evaluation)
Week 11-12: Writeup + presentation prep
```

---

## Copilot Tips

- **Always paste the context block** at the top of each session
- **One step at a time** — give Copilot one step number and its full spec, nothing more
- **After each step**, run the code before moving to the next step
- **Step 2.6 (inspect.py) is mandatory** — do not skip it. Bad chunks produce bad retrieval and you won't know until evaluation if you don't spot-check early
- **Step 6.2 (integration test) is mandatory** — run it before building the interface. Fix pipeline issues before they become UI issues
- **If Copilot drifts toward LangChain for retrieval or generation**, remind it: "retrieval and generation are custom — do not use LangChain chains or LangChain LLM wrappers for these steps"
