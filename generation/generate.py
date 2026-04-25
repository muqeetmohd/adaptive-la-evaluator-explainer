import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_OLLAMA_MODEL = "mistral:instruct"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def generate_explanation(
    prompt_messages: dict,
    model: str = None,
    ollama_url: str = OLLAMA_URL,
) -> str:
    groq_key = os.getenv("GROQ_API_KEY")

    if groq_key:
        return _generate_groq(prompt_messages, model or DEFAULT_GROQ_MODEL, groq_key)
    else:
        return _generate_ollama(prompt_messages, model or DEFAULT_OLLAMA_MODEL, ollama_url)


def _generate_groq(prompt_messages: dict, model: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": prompt_messages["messages"],
    }
    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot connect to Groq API. Check your internet connection.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Groq API error: {e} — {response.text}")

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, TypeError, IndexError):
        raise RuntimeError(f"Malformed response from Groq: {data}")


def _generate_ollama(prompt_messages: dict, model: str, ollama_url: str) -> str:
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
