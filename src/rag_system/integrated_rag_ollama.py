import sys
sys.path.append('src')

from embeddings.log_embedder import LogEmbedder
from vector_db.vector_database import VectorDatabase
from rag_system.basic_rag_ollama import BasicRAGOllama
from typing import Dict

class ICSLogQueryGPTOllama:
    """
    Complete integrated system with Ollama
    
    Pipeline:
    1. User asks question
    2. Embed question with BERT
    3. Search vector DB for similar logs
    4. Generate answer with Llama 3.1
    """
    
    def __init__(self, vector_db_path: str, metadata_path: str, 
                 model_name: str = "llama3.1:8b"):
        """
        Initialize complete system
        
        Args:
            vector_db_path: Path to FAISS index
            metadata_path: Path to metadata
            model_name: Ollama model name
        """
        print("🚀 Initializing ICS-LogQueryGPT with Ollama...")
        
        # Load embedder (from Week 1)
        print("   Loading BERT embedder...")
        self.embedder = LogEmbedder()
        
        # Load vector database
        print("   Loading vector database...")
        self.vector_db = VectorDatabase()
        self.vector_db.load(vector_db_path, metadata_path)
        
        # Initialize RAG
        print("   Initializing RAG system...")
        self.rag = BasicRAGOllama(model_name=model_name)
        
        print("✅ System ready!")
    
    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        Complete query pipeline
        
        Args:
            question: User's question in natural language
            top_k: Number of logs to retrieve
            
        Returns:
            Dict with answer and metadata
        """
        print(f"\n🔍 Processing: '{question}'")
        
        # Step 1: Embed question
        print("1️⃣ Creating question embedding...")
        question_emb = self.embedder.embed_single_log(question)
        
        # Step 2: Search vector DB
        print(f"2️⃣ Searching for top {top_k} similar logs...")
        retrieved_logs = self.vector_db.search(question_emb, k=top_k)
        
        print(f"   Found {len(retrieved_logs)} relevant logs")
        for i, log in enumerate(retrieved_logs[:3], 1):
            print(f"   {i}. Score: {log['similarity_score']:.3f} - {log['log_text'][:50]}...")
        
        # Step 3: Generate answer
        print("3️⃣ Generating answer with Llama 3.1...")
        result = self.rag.generate_answer(question, retrieved_logs)
        
        print("✅ Complete!")
        return result


# === TEST INTEGRATED SYSTEM ===
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Integrated ICS-LogQueryGPT")
    print("=" * 60)
    
    # Initialize system
    print("\n🔧 Loading system...")
    system = ICSLogQueryGPTOllama(
        vector_db_path='data/vector_db/HDFS_index.faiss',
        metadata_path='data/vector_db/HDFS_metadata.pkl',
        model_name='llama3.1:8b'
    )
    
    # Test questions
    questions = [
        "Show me authentication failures",
        "What errors occurred in the system?",
        "Are there any timeout issues?"
    ]
    
    print("\n" + "=" * 60)
    print("Running Test Queries")
    print("=" * 60)
    
    for q in questions:
        result = system.query(q, top_k=5)
        
        print("\n" + "-" * 60)
        print(f"❓ Question: {q}")
        print("-" * 60)
        print(f"💬 Answer:\n{result['answer']}")
        print(f"\n⏱️  Time: {result.get('generation_time', 0):.2f}s")
        print("-" * 60)
    
    print("\n✅ All tests complete!")