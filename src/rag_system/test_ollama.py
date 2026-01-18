import requests
import json


def test_ollama_connection():
    """Test Ollama API connection"""

    print(" Testing Ollama connection...")

    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "llama3.1:8b",
        "prompt": "Say 'API connected!' if you can read this.",
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            result = response.json()
            print(f" {result['response']}")
            print(f" Generation time: {result.get('total_duration', 0) / 1e9:.2f}s")
        else:
            print(f" Error: {response.status_code}")

    except Exception as e:
        print(f" Error: {e}")
        print(" Make sure Ollama is running: ollama serve")


if __name__ == "__main__":
    test_ollama_connection()
