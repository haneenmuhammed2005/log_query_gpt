import time
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import os


class BasicRAGOllama:
    """
    LLM interface for Retrieval Augmented Generation (RAG)
    Primary: Groq (llama-3.1-8b-instant) — fastest, free
    Fallback: Gemini 1.5 Flash — if Groq fails
    """

    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.model_name = model_name

        # Primary - Groq (fastest ~1-3s)
        primary_llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            api_key=os.environ.get("GROQ_API_KEY")
        )

        # Fallback - Gemini Flash
        fallback_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=os.environ.get("GOOGLE_API_KEY")
        )

        self.llm = primary_llm.with_fallbacks([fallback_llm])

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

    def generate_answer_from_prompt(self, prompt: str) -> Dict:
        return self._send(prompt)

    def _send(self, prompt: str) -> Dict:
        start = time.time()
        try:
            response = self.llm.invoke(prompt)
            return {
                "answer": response.content.strip(),
                "generation_time": time.time() - start,
                "model": self.model_name,
                "error": False
            }
        except Exception as e:
            return {
                "answer": f"LLM error: {str(e)}",
                "error": True,
                "generation_time": time.time() - start
            }


if __name__ == "__main__":
    rag = BasicRAGOllama()
    logs = [
        {"log_text": "authentication failed for user admin", "similarity_score": 0.94},
        {"log_text": "modbus write multiple coils failed", "similarity_score": 0.89}
    ]
    print(rag.generate_answer("Are there security issues?", logs)["answer"])
