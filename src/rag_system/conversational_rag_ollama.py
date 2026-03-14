import sys
import os
sys.path.append(os.path.abspath("src"))

from rag_system.enhanced_rag_ollama import EnhancedRAGOllama
from typing import List, Dict, Optional
import json
from datetime import datetime
import time

class ConversationalRAGOllama(EnhancedRAGOllama):
    """RAG system with conversation memory and context management"""
    
    def __init__(self, 
                 model_name: str = "llama3:8b-instruct-q4_0",
                 max_history: int = 5):
        super().__init__(model_name)
        self.max_history = max_history
        self.conversation_id = None
        self.start_time = None
    
    def start_conversation(self, conversation_id: Optional[str] = None):
        """Start a new conversation session"""
        self.conversation_id = conversation_id or f"conv_{int(datetime.now().timestamp())}"
        self.start_time = datetime.now()
        self.conversation_history = []
        self.conversation_started = True
        print(f"💬 Started conversation: {self.conversation_id}")
    
    def add_to_history(self, question: str, answer: str, metadata: Optional[Dict] = None):
        """
        Add Q&A exchange to conversation history
        
        Args:
            question: User's question
            answer: Assistant's answer
            metadata: Additional metadata (logs, mode, etc.)
        """
        self.conversation_history.append({
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        })
        
        # Keep only last N exchanges to manage context size
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def build_conversation_context(self, include_full_answers: bool = False) -> str:
        """
        Build context string from conversation history
        
        Args:
            include_full_answers: Include full answers or just summaries
            
        Returns:
            Formatted conversation history
        """
        if not self.conversation_history:
            return ""
        
        context = "\n=== CONVERSATION HISTORY ===\n"
        context += f"(Last {len(self.conversation_history)} exchanges)\n\n"
        
        for i, exchange in enumerate(self.conversation_history, 1):
            context += f"Exchange {i}:\n"
            context += f"  User: {exchange['question']}\n"
            
            if include_full_answers:
                answer = exchange['answer']
            else:
                # Truncate long answers
                answer = exchange['answer'][:200] + "..." if len(exchange['answer']) > 200 else exchange['answer']
            
            context += f"  Assistant: {answer}\n"
            context += "-" * 60 + "\n"
        
        context += "\n=== CURRENT QUESTION ===\n"
        return context
    
    def generate_with_context(self,
                             question: str,
                             retrieved_logs: List[Dict],
                             mode: str = 'analysis',
                             use_conversation_context: bool = True,
                             temperature: float = 0.7,
                             max_tokens: int = 1000) -> Dict:
        """
        Generate answer with conversation context
        
        Args:
            question: Current question
            retrieved_logs: Retrieved log entries
            mode: Generation mode
            use_conversation_context: Whether to include conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dict with answer and metadata
        """
        # Build base prompt
        if mode == 'analysis':
            base_prompt = self.prompt_engineer.create_analysis_prompt(
                question, retrieved_logs
            )
        elif mode == 'summary':
            base_prompt = self.prompt_engineer.create_summary_prompt(
                retrieved_logs
            )
        elif mode == 'security':
            base_prompt = self.prompt_engineer.create_security_prompt(
                retrieved_logs
            )
        elif mode == 'troubleshooting':
            base_prompt = self.prompt_engineer.create_troubleshooting_prompt(
                retrieved_logs, question
            )
        else:
            base_prompt = self.prompt_engineer.create_analysis_prompt(
                question, retrieved_logs
            )
        
        # Add conversation context if requested and available
        if use_conversation_context and self.conversation_history:
            conv_context = self.build_conversation_context(include_full_answers=False)
            
            # Insert context before the analysis instructions
            prompt = base_prompt.replace(
                "=== USER QUESTION ===",
                conv_context + "\n=== USER QUESTION ==="
            )
            
            # Add instruction to consider history
            prompt += "\n\nIMPORTANT: Consider the conversation history when formulating your answer. If the current question refers to previous exchanges (e.g., 'What about...', 'And also...'), incorporate that context. However, always prioritize the current question and the retrieved logs."
        else:
            prompt = base_prompt
        
        # Generate answer using Ollama API
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1
            }
        }
        
        try:
            import requests
            
            start_time = time.time()
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['response']
                generation_time = time.time() - start_time
                
                # Add to conversation history
                self.add_to_history(question, answer, {
                    'mode': mode,
                    'logs_count': len(retrieved_logs),
                    'generation_time': generation_time
                })
                
                # Store in generation stats
                stats = {
                    'question': question,
                    'answer': answer,
                    'mode': mode,
                    'retrieved_logs': retrieved_logs,
                    'generation_time': generation_time,
                    'conversation_length': len(self.conversation_history),
                    'conversation_id': self.conversation_id,
                    'model': self.model_name,
                    'temperature': temperature,
                    'timestamp': time.time()
                }
                self.generation_stats.append(stats)
                
                return stats
            else:
                return {
                    'error': True,
                    'message': f"HTTP {response.status_code}",
                    'question': question
                }
        
        except Exception as e:
            return {
                'error': True,
                'message': str(e),
                'question': question
            }
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of current conversation"""
        if not self.conversation_history:
            return {"message": "No conversation yet"}
        
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            'conversation_id': self.conversation_id,
            'total_exchanges': len(self.conversation_history),
            'duration_seconds': duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'modes_used': list(set(ex['metadata'].get('mode', 'unknown') 
                                  for ex in self.conversation_history)),
            'total_logs_analyzed': sum(ex['metadata'].get('logs_count', 0) 
                                      for ex in self.conversation_history)
        }
    
    def clear_history(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.conversation_id = None
        self.start_time = None
        self.conversation_started = False
        print("🗑️ Conversation history cleared")
    
    def export_conversation(self, filepath: str):
        """Export conversation to JSON file"""
        export_data = {
            'conversation_id': self.conversation_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'exchanges': self.conversation_history,
            'summary': self.get_conversation_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"💾 Conversation exported to: {filepath}")


# Testing and demonstration
if __name__ == "__main__":
    print("="*70)
    print("TESTING CONVERSATIONAL RAG")
    print("="*70)
    
    conv_rag = ConversationalRAGOllama(model_name='llama3:8b-instruct-q4_0')
    conv_rag.start_conversation()
    
    # Test logs
    test_logs = [
        {
            'log_text': 'authentication failed for user admin from IP 192.168.1.100',
            'similarity_score': 0.95,
            'protocols': 'ssh',
            'severity': 'high'
        },
        {
            'log_text': 'repeated login attempts detected from same IP',
            'similarity_score': 0.89,
            'protocols': 'ssh',
            'severity': 'critical'
        }
    ]
    
    # First question
    print("\n1️⃣ FIRST QUESTION")
    print("-"*70)
    result1 = conv_rag.generate_with_context(
        "What authentication issues do you see?",
        test_logs
    )
    
    if not result1.get('error'):
        print(f"Q: {result1['question']}")
        print(f"A: {result1['answer'][:200]}...")
        print(f"⏱️ Time: {result1['generation_time']:.2f}s")
        print(f"💬 Conversation length: {result1['conversation_length']}\n")
    else:
        print(f"❌ Error: {result1.get('message', 'Unknown error')}")
    
    # Follow-up question (should use context)
    print("\n2️⃣ FOLLOW-UP QUESTION")
    print("-"*70)
    result2 = conv_rag.generate_with_context(
        "Which IP address was it from?",
        test_logs
    )
    
    if not result2.get('error'):
        print(f"Q: {result2['question']}")
        print(f"A: {result2['answer'][:200]}...")
        print(f"💬 Conversation length: {result2['conversation_length']}\n")
    else:
        print(f"❌ Error: {result2.get('message', 'Unknown error')}")
    
    # Another follow-up
    print("\n3️⃣ SECURITY ANALYSIS")
    print("-"*70)
    result3 = conv_rag.generate_with_context(
        "Is this a security concern?",
        test_logs,
        mode='security'
    )
    
    if not result3.get('error'):
        print(f"Q: {result3['question']}")
        print(f"A: {result3['answer'][:200]}...")
        print(f"💬 Conversation length: {result3['conversation_length']}\n")
    else:
        print(f"❌ Error: {result3.get('message', 'Unknown error')}")
    
    # Conversation summary
    print("\n4️⃣ CONVERSATION SUMMARY")
    print("-"*70)
    summary = conv_rag.get_conversation_summary()
    print(json.dumps(summary, indent=2))
    
    # Export conversation
    print("\n5️⃣ EXPORTING CONVERSATION")
    print("-"*70)
    conv_rag.export_conversation('conversation_export.json')
    
    print("\n✅ All conversational tests completed!")