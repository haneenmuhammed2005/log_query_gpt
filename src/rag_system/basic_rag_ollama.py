import requests
import json
from typing import List, Dict

class BasicRAGOllama:
    """
    Simple RAG system for log analysis using Ollama + Llama 3.1
    
    RAG = Retrieval Augmented Generation
    - Retrieves relevant logs
    - Generates answer using those logs as context
    """
    
    def __init__(self, model_name: str = "llama3.1:8b"):
        """
        Initialize RAG system
        
        Args:
            model_name: Ollama model to use
        """
        self.model_name = model_name
        self.base_url = "http://localhost:11434/api/generate"
    
    def create_prompt(self, question: str, retrieved_logs: List[Dict]) -> str:
        """
        Create prompt with retrieved logs as context
        
        Args:
            question: User's question
            retrieved_logs: List of similar logs from vector DB
            
        Returns:
            Formatted prompt for LLM
        """
        # Build context from retrieved logs
        context = "Here are relevant log entries:\n\n"
        
        for i, log in enumerate(retrieved_logs, 1):
            context += f"Log {i} (Similarity: {log['similarity_score']:.2f}):\n"
            context += f"{log['log_text']}\n"
            context += "-" * 50 + "\n"
        
        # Create full prompt
        prompt = f"""{context}

Based on the above logs, answer this question:

Question: {question}

Instructions:
1. Analyze the log entries carefully
2. Provide a clear, concise answer
3. Cite specific logs if relevant (e.g., "Log 1 shows...")
4. If logs don't contain enough information, say so
5. Be specific and technical

Answer:"""
        
        return prompt
    
    def generate_answer(self, question: str, retrieved_logs: List[Dict]) -> Dict:
        """
        Generate answer using Llama 3.1 via Ollama
        
        Args:
            question: User's question
            retrieved_logs: Retrieved logs from vector DB
            
        Returns:
            Dict with answer, metadata, etc.
        """
        # Create prompt
        prompt = self.create_prompt(question, retrieved_logs)
        
        print("🤖 Generating answer with Llama 3.1...")
        
        # Prepare request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,  # Get complete response at once
            "options": {
                "temperature": 0.7,  # Creativity level (0-1)
                "num_predict": 500   # Max tokens in response
            }
        }
        
        try:
            # Call Ollama API
            response = requests.post(self.base_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                answer = result['response']
                
                # Estimate token usage
                tokens = len(prompt.split()) + len(answer.split())
                
                return {
                    'question': question,
                    'answer': answer,
                    'retrieved_logs': retrieved_logs,
                    'tokens_used': tokens,
                    'generation_time': result.get('total_duration', 0) / 1e9,
                    'model': self.model_name,
                    'error': False
                }
            else:
                return {
                    'question': question,
                    'answer': f"Error: HTTP {response.status_code}",
                    'error': True
                }
        
        except Exception as e:
            return {
                'question': question,
                'answer': f"Error: {str(e)}",
                'error': True
            }


# === TEST THE RAG SYSTEM ===
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Basic RAG with Ollama")
    print("=" * 60)
    
    # Initialize RAG
    print("\n1️⃣ Initializing RAG system...")
    rag = BasicRAGOllama()
    
    # Create test logs
    test_logs = [
        {
            'log_text': 'authentication failed for user admin from IP 192.168.1.100',
            'similarity_score': 0.95
        },
        {
            'log_text': 'connection timeout after 30 seconds',
            'similarity_score': 0.82
        },
        {
            'log_text': 'permission denied for user guest',
            'similarity_score': 0.78
        }
    ]
    
    # Test question
    question = "What security issues are shown in the logs?"
    
    print(f"\n2️⃣ Asking: {question}")
    print("\n3️⃣ Generating answer...")
    
    result = rag.generate_answer(question, test_logs)
    
    # Display result
    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"\n💬 Answer:\n{result['answer']}")
    print(f"\n⏱️  Time: {result.get('generation_time', 0):.2f}s")
    print(f"📊 Tokens: ~{result.get('tokens_used', 0)}")
    print("\n✅ Test complete!")