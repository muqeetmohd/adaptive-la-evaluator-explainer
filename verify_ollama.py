import requests
import sys

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "mistral:instruct"


def verify_ollama():
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Say 'hello' in one word."}],
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data["message"]["content"]
        print(f"Response: {content}")
        print("Ollama connection verified")
    except requests.exceptions.ConnectionError:
        sys.exit(
            "ERROR: Cannot connect to Ollama at http://localhost:11434. "
            "Make sure Ollama is running: `ollama serve`"
        )
    except requests.exceptions.HTTPError as e:
        sys.exit(f"ERROR: HTTP error from Ollama: {e}")
    except KeyError:
        sys.exit(f"ERROR: Malformed response from Ollama: {response.text}")


if __name__ == "__main__":
    verify_ollama()
