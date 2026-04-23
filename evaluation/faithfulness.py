from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper


def setup_ragas_with_local_mistral():
    llm = Ollama(model="mistral:instruct")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return {
        "llm": LangchainLLMWrapper(llm),
        "embeddings": LangchainEmbeddingsWrapper(embeddings),
    }


def score_faithfulness(
    question: str,
    answer: str,
    contexts: list,
) -> float:
    evaluator = setup_ragas_with_local_mistral()

    dataset = Dataset.from_dict({
        "question": [question],
        "answer": [answer],
        "contexts": [contexts],
    })

    result = evaluate(
        dataset,
        metrics=[faithfulness],
        llm=evaluator["llm"],
        embeddings=evaluator["embeddings"],
    )

    score = float(result["faithfulness"])

    if score < 0.75:
        print(f"WARNING: Low faithfulness score ({score:.2f}) for question: {question}")

    return score
