import requests
import time
from typing import List, Dict


class BasicRAGOllama:
    """
    Ollama interface for Retrieval Augmented Generation (RAG)

    Supports:
    1. Simple RAG (question + retrieved logs)
    2. Advanced RAG (pre-built prompt from PromptEngineer)
    """

    def __init__(self, model_name: str = "llama3:8b-instruct-q4_0"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434/api/generate"

    # -------------------------------------------------
    # WEEK 2 — BASIC RAG
    # -------------------------------------------------
    def create_prompt(self, question: str, retrieved_logs: List[Dict]) -> str:
        context = "Here are relevant log entries:\n\n"

        for i, log in enumerate(retrieved_logs, 1):
            context += f"Log Entry {i} (Score {log['similarity_score']:.3f}):\n"
            context += f"{log['log_text']}\n"
            context += "-" * 50 + "\n"

        return f"""{context}

Question:
{question}

Instructions:
- Reference specific logs
- Explain clearly
- Say if evidence is insufficient

Answer:
"""

    def generate_answer(self, question: str, retrieved_logs: List[Dict]) -> Dict:
        prompt = self.create_prompt(question, retrieved_logs)
        return self._send(prompt)

    # -------------------------------------------------
    # WEEK 3 — ADVANCED PROMPT
    # -------------------------------------------------
    def generate_answer_from_prompt(self, prompt: str) -> Dict:
        return self._send(prompt)

    # -------------------------------------------------
    # LOW-LEVEL OLLAMA CALL (SAFE)
    # -------------------------------------------------
    def _send(self, prompt: str) -> Dict:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 300   # 🔴 memory-safe
            }
        }

        start = time.time()

        try:
            response = requests.post(self.base_url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()

            return {
                "answer": data.get("response", "").strip(),
                "generation_time": time.time() - start,
                "model": self.model_name,
                "error": False
            }

        except Exception as e:
            return {
                "answer": f"Ollama error: {str(e)}",
                "error": True
            }


# -------------------------------------------------
# LOCAL TEST
# -------------------------------------------------
if __name__ == "__main__":
    rag = BasicRAGOllama()

    logs = [
        {"log_text": "authentication failed for user admin", "similarity_score": 0.94},
        {"log_text": "modbus write multiple coils failed", "similarity_score": 0.89}
    ]

    print(rag.generate_answer(
        "Are there security issues?",
        logs
    )["answer"])
