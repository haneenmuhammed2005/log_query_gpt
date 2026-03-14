import sys
sys.path.append("src")

from typing import Dict
from src.embeddings.log_embedder import LogEmbedder
from src.vector_db.vector_database import VectorDatabase
from src.rag_system.basic_rag_ollama import BasicRAGOllama
from src.rag_system.advanced_prompts_ollama import PromptEngineerOllama


class ICSLogQueryGPTOllama:
    """
    Fully integrated ICS Log Query System
    """

    def __init__(
        self,
        vector_db_path: str,
        metadata_path: str,
        model_name: str = "llama3:8b-instruct-q4_0"
    ):
        print("🚀 Initializing ICS-LogQueryGPT")

        self.embedder = LogEmbedder()
        self.vector_db = VectorDatabase()
        self.vector_db.load(vector_db_path, metadata_path)

        self.prompt_engineer = PromptEngineerOllama()
        self.rag = BasicRAGOllama(model_name=model_name)

        print("✅ System ready")

    def query(self, question: str, top_k: int = 5) -> Dict:
        print(f"\n🔍 Question: {question}")

        q_emb = self.embedder.embed_single_log(question)
        logs = self.vector_db.search(q_emb, k=top_k)

        prompt = self.prompt_engineer.create_analysis_prompt(
            question, logs
        )

        result = self.rag.generate_answer_from_prompt(prompt)

        return {
            "question": question,
            "answer": result["answer"],
            "generation_time": result.get("generation_time", 0),
            "model": self.rag.model_name
        }


# -------------------------------------------------
# TEST
# -------------------------------------------------
if __name__ == "__main__":
    system = ICSLogQueryGPTOllama(
        "D:/Projects/log_query_gpt/data/vector_db/HDFS_index.faiss",
        "D:/Projects/log_query_gpt/data/vector_db/HDFS_metadata.pkl"
    )

    print(system.query(
        "Are there authentication failures?",
        top_k=5
    )["answer"])
