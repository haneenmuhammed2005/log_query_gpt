import sys
import os
sys.path.append(os.path.abspath("src"))

import requests
import json
from typing import List, Dict, Optional
from rag_system.advanced_prompts_ollama import PromptEngineerOllama
import time

class EnhancedRAGOllama:
    """Enhanced RAG with advanced prompting and query optimization"""
    
    def __init__(self, model_name: str = "llama3:8b-instruct-q4_0"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434/api/generate"
        self.prompt_engineer = PromptEngineerOllama()
        self.generation_stats = []
        self.conversation_history = []
        self.conversation_started = False
    
    def generate_answer(self, 
                       question: str,
                       retrieved_logs: List[Dict],
                       mode: str = 'analysis',
                       temperature: float = 0.7,
                       max_tokens: int = 1000) -> Dict:
        """
        Generate answer using Llama 3.1
        
        Args:
            question: User's question
            retrieved_logs: Retrieved log entries with metadata
            mode: 'analysis', 'summary', 'security', or 'troubleshooting'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with answer and metadata
        """
        # Select appropriate prompt based on mode
        if mode == 'analysis':
            prompt = self.prompt_engineer.create_analysis_prompt(
                question, retrieved_logs
            )
        elif mode == 'summary':
            prompt = self.prompt_engineer.create_summary_prompt(
                retrieved_logs
            )
        elif mode == 'security':
            prompt = self.prompt_engineer.create_security_prompt(
                retrieved_logs
            )
        elif mode == 'troubleshooting':
            prompt = self.prompt_engineer.create_troubleshooting_prompt(
                retrieved_logs, question
            )
        else:
            prompt = self.prompt_engineer.create_analysis_prompt(
                question, retrieved_logs
            )
        
        print(f"🤖 Generating {mode} answer with {self.model_name}...")
        
        # Prepare Ollama API payload
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
                
                # Calculate statistics
                prompt_tokens = len(prompt.split())
                response_tokens = len(answer.split())
                
                stats = {
                    'question': question,
                    'answer': answer,
                    'mode': mode,
                    'retrieved_logs': retrieved_logs,
                    'prompt_tokens': prompt_tokens,
                    'response_tokens': response_tokens,
                    'total_tokens': prompt_tokens + response_tokens,
                    'generation_time': generation_time,
                    'tokens_per_second': response_tokens / generation_time if generation_time > 0 else 0,
                    'model': self.model_name,
                    'temperature': temperature,
                    'timestamp': time.time()
                }
                
                # Store for analytics
                self.generation_stats.append(stats)
                
                return stats
            else:
                return {
                    'question': question,
                    'answer': f"Error: HTTP {response.status_code} - {response.text}",
                    'error': True,
                    'status_code': response.status_code
                }
        
        except requests.Timeout:
            return {
                'question': question,
                'answer': "Error: Request timed out. The model may be overloaded or the query too complex.",
                'error': True
            }
        except Exception as e:
            return {
                'question': question,
                'answer': f"Error: {str(e)}",
                'error': True,
                'exception': str(e)
            }

    def start_conversation(self):
        """Start a new conversation"""
        self.conversation_history = []
        self.conversation_started = True

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def export_conversation(self, filename: str):
        """Export conversation to JSON file"""
        with open(filename, "w") as f:
            json.dump(self.conversation_history, f, indent=2)

    def get_conversation_summary(self):
        """Get summary of current conversation"""
        return {
            "total_exchanges": len(self.conversation_history),
            "total_logs_analyzed": 0,
            "start_time": None
        }
    
    def generate_with_context(self,
                             question: str,
                             retrieved_logs: List[Dict],
                             mode: str = 'analysis',
                             use_history: bool = True,
                             temperature: float = 0.7,
                             max_tokens: int = 1000) -> Dict:
        """
        Generate answer with conversation context
        
        Args:
            question: User's question
            retrieved_logs: Retrieved log entries
            mode: Response mode
            use_history: Whether to include conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with answer and metadata
        """
        # Build context from conversation history
        context = ""
        if use_history and self.conversation_history:
            context = "\n\nPrevious conversation:\n"
            for exchange in self.conversation_history[-3:]:  # Last 3 exchanges
                context += f"Q: {exchange['question']}\n"
                context += f"A: {exchange['answer'][:200]}...\n\n"
        
        # Generate answer with context
        result = self.generate_answer(
            question=question,
            retrieved_logs=retrieved_logs,
            mode=mode,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Store in conversation history
        if not result.get('error'):
            self.conversation_history.append({
                'question': question,
                'answer': result['answer'],
                'mode': mode,
                'timestamp': time.time(),
                'retrieved_logs_count': len(retrieved_logs)
            })
        
        return result
    
    def multi_query_expansion(self, question: str, n_queries: int = 3) -> List[str]:
        """
        Expand user query into multiple variations for better retrieval
        
        Uses Llama 3.1 to generate semantically related queries
        """
        expansion_prompt = f"""Given this question about ICS/SCADA logs:
"{question}"

Generate {n_queries} related questions that would help find relevant log entries. Each question should explore a different aspect:

1. A more specific technical version (focusing on protocols, error codes, or systems)
2. A broader operational version (focusing on impact or symptoms)
3. A security-focused version (if applicable)

Requirements:
- Each question must be complete and specific
- Focus on ICS/SCADA context
- Make them diverse but related
- Format: Return ONLY the questions, numbered 1-{n_queries}, one per line
- No explanations, just the questions

Example format:
1. [First question here]
2. [Second question here]
3. [Third question here]

Your {n_queries} questions:"""
        
        payload = {
            "model": self.model_name,
            "prompt": expansion_prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "num_predict": 200
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result['response']
                
                # Parse numbered questions
                lines = text.strip().split('\n')
                questions = []
                
                for line in lines:
                    # Remove numbering and clean
                    clean_line = line.strip()
                    if clean_line and any(c.isalpha() for c in clean_line):
                        # Remove leading numbers, dots, and spaces
                        clean_line = clean_line.lstrip('0123456789.)-  ')
                        if clean_line and len(clean_line) > 10:  # Min length check
                            questions.append(clean_line)
                
                # Return up to n_queries unique questions
                unique_questions = list(dict.fromkeys(questions))[:n_queries]
                
                # Always include original question
                if question not in unique_questions:
                    unique_questions.insert(0, question)
                
                return unique_questions[:n_queries + 1]
            else:
                return [question]  # Fallback to original
                
        except Exception as e:
            print(f"⚠️ Query expansion failed: {e}")
            return [question]  # Fallback to original
    
    def get_generation_statistics(self) -> Dict:
        """Get statistics about all generations"""
        if not self.generation_stats:
            return {"message": "No generations yet"}
        
        total_gens = len(self.generation_stats)
        total_time = sum(s['generation_time'] for s in self.generation_stats)
        total_tokens = sum(s['total_tokens'] for s in self.generation_stats)
        avg_tokens_per_sec = sum(s['tokens_per_second'] for s in self.generation_stats) / total_gens
        
        return {
            'total_generations': total_gens,
            'total_generation_time': total_time,
            'average_generation_time': total_time / total_gens,
            'total_tokens': total_tokens,
            'average_tokens_per_generation': total_tokens / total_gens,
            'average_tokens_per_second': avg_tokens_per_sec,
            'mode_distribution': self._count_modes()
        }
    
    def _count_modes(self) -> Dict:
        """Count usage of each mode"""
        modes = {}
        for stat in self.generation_stats:
            mode = stat.get('mode', 'unknown')
            modes[mode] = modes.get(mode, 0) + 1
        return modes


# Testing and demonstration
if __name__ == "__main__":
    print("="*70)
    print("TESTING ENHANCED RAG SYSTEM")
    print("="*70)
    
    rag = EnhancedRAGOllama(model_name='llama3:8b-instruct-q4_0')
    
    # Test logs
    test_logs = [
        {
            'log_text': 'authentication failed for user admin from 192.168.1.100 after 3 attempts',
            'protocols': 'ssh',
            'severity': 'high',
            'similarity_score': 0.95
        },
        {
            'log_text': 'modbus write multiple coils failed device 5 function code 15',
            'protocols': 'modbus',
            'severity': 'medium',
            'similarity_score': 0.87
        }
    ]
    
    # Test 1: Analysis mode
    print("\n1️⃣ TESTING ANALYSIS MODE")
    print("-"*70)
    result = rag.generate_answer(
        "What security issues do you see?",
        test_logs,
        mode='analysis'
    )
    
    if not result.get('error'):
        print(f"💬 Answer:\n{result['answer'][:300]}...")
        print(f"\n⏱️ Generation time: {result['generation_time']:.2f}s")
        print(f"🔢 Tokens/second: {result['tokens_per_second']:.1f}")
    else:
        print(f"❌ Error: {result['answer']}")
    
    # Test 2: Summary mode
    print("\n\n2️⃣ TESTING SUMMARY MODE")
    print("-"*70)
    result = rag.generate_answer(
        "",  # No question needed for summary
        test_logs,
        mode='summary'
    )
    
    if not result.get('error'):
        print(f"💬 Summary:\n{result['answer'][:300]}...")
    
    # Test 3: Query expansion
    print("\n\n3️⃣ TESTING QUERY EXPANSION")
    print("-"*70)
    original_query = "Show me authentication errors"
    expanded = rag.multi_query_expansion(original_query)
    
    print(f"Original query: {original_query}")
    print(f"\nExpanded queries ({len(expanded)}):")
    for i, q in enumerate(expanded, 1):
        print(f"  {i}. {q}")
    
    # Test 4: Statistics
    print("\n\n4️⃣ GENERATION STATISTICS")
    print("-"*70)
    stats = rag.get_generation_statistics()
    print(json.dumps(stats, indent=2))
    
    print("\n✅ All tests completed!")