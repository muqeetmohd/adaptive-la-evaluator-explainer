import os
import requests
from dotenv import load_dotenv

load_dotenv()

_GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_OLLAMA_MODEL = "mistral:instruct"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def generate_explanation(
    prompt_messages: dict,
    model: str = None,
    ollama_url: str = OLLAMA_URL,
) -> str:
    if _GROQ_API_KEY:
        return _call_api(
            url=GROQ_API_URL,
            payload={"model": model or DEFAULT_GROQ_MODEL, "messages": prompt_messages["messages"]},
            headers={"Authorization": f"Bearer {_GROQ_API_KEY}", "Content-Type": "application/json"},
            response_key=lambda d: d["choices"][0]["message"]["content"],
            provider="Groq",
            timeout=60,
        )
    return _call_api(
        url=ollama_url,
        payload={"model": model or DEFAULT_OLLAMA_MODEL, "messages": prompt_messages["messages"], "stream": False},
        headers={},
        response_key=lambda d: d["message"]["content"],
        provider="Ollama",
        timeout=120,
    )


def _call_api(url: str, payload: dict, headers: dict, response_key, provider: str, timeout: int) -> str:
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Cannot connect to {provider}. Check your connection.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"{provider} API error: {e} — {response.text}")

    data = response.json()
    try:
        return response_key(data)
    except (KeyError, TypeError, IndexError):
        raise RuntimeError(f"Malformed response from {provider}: {data}")
