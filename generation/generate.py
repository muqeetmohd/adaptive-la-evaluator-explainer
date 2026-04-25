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


def generate_explanation_stream(prompt_messages: dict, model: str = None):
    """Yields text chunks from Groq (falls back to full response if Ollama)."""
    if _GROQ_API_KEY:
        yield from _stream_groq(prompt_messages["messages"], model or DEFAULT_GROQ_MODEL)
    else:
        yield generate_explanation(prompt_messages, model)


def _stream_groq(messages: list, model: str):
    import json as _json
    try:
        resp = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {_GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "stream": True},
            stream=True,
            timeout=60,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot connect to Groq. Check your connection.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Groq API error: {e} — {resp.text}")

    for raw in resp.iter_lines():
        if not raw:
            continue
        line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        if not line.startswith("data: "):
            continue
        payload = line[6:]
        if payload == "[DONE]":
            break
        try:
            delta = _json.loads(payload)["choices"][0]["delta"].get("content", "")
            if delta:
                yield delta
        except (KeyError, IndexError, ValueError):
            pass


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
