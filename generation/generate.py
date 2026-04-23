import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "mistral:instruct"


def generate_explanation(
    prompt_messages: dict,
    model: str = DEFAULT_MODEL,
    ollama_url: str = OLLAMA_URL,
) -> str:
    payload = {
        "model": model,
        "messages": prompt_messages["messages"],
        "stream": False,
    }
    try:
        response = requests.post(ollama_url, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama at http://localhost:11434. "
            "Make sure Ollama is running: `ollama serve`"
        )
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error from Ollama: {e}")

    data = response.json()
    try:
        return data["message"]["content"]
    except (KeyError, TypeError):
        raise RuntimeError(f"Malformed response from Ollama: {data}")
