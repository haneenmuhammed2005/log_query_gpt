from typing import List, Dict, Optional


class PromptEngineerOllama:
    """
    Creates expert-level ICS prompts.
    DOES NOT talk to Ollama.
    """

    def __init__(self):
        self.base_prompt = """You are an Industrial Control System (ICS) security analyst
with deep experience in SCADA, OT networks, and industrial protocols.

Rules:
- Reference specific log entries
- Explain in simple terms
- Prioritize safety and availability
- Avoid speculation
"""

    # -------------------------------------------------
    # ANALYSIS PROMPT
    # -------------------------------------------------
    def create_analysis_prompt(self, question: str, logs: List[Dict]) -> str:
        context = "=== LOG ENTRIES ===\n"

        for i, log in enumerate(logs, 1):
            context += (
                f"\nLog {i}:\n"
                f"Text: {log['log_text']}\n"
                f"Protocol: {log.get('protocols', 'unknown')}\n"
                f"Severity: {log.get('severity', 'unknown')}\n"
                f"Score: {log['similarity_score']:.3f}\n"
            )

        return f"""{self.base_prompt}

{context}

Question:
{question}

Explain:
- What happened
- Why it happened
- Impact
- Recommended actions

Answer:
"""

    # -------------------------------------------------
    # SECURITY PROMPT
    # -------------------------------------------------
    def create_security_prompt(self, logs: List[Dict]) -> str:
        context = ""

        for i, log in enumerate(logs, 1):
            context += f"{i}. [{log.get('protocols','unknown')}] {log['log_text']}\n"

        return f"""{self.base_prompt}

Security review these logs:

{context}

Identify:
- Authentication failures
- Unauthorized access
- Dangerous protocol usage

Give mitigation steps.
"""

    # -------------------------------------------------
    # SUMMARY PROMPT
    # -------------------------------------------------
    def create_summary_prompt(self, logs: List[Dict]) -> str:
        lines = [
            f"{i}. {log['log_text']}"
            for i, log in enumerate(logs, 1)
        ]

        return f"""{self.base_prompt}

Summarize the following logs:

{chr(10).join(lines)}

Provide:
- Key events
- Severity
- Recommended actions
"""

    # -------------------------------------------------
    # TROUBLESHOOTING PROMPT
    # -------------------------------------------------
    def create_troubleshooting_prompt(self, question: str, logs: List[Dict]) -> str:
        """Create troubleshooting focused prompt"""
        context = "=== SYSTEM LOGS ===\n"

        for i, log in enumerate(logs, 1):
            context += (
                f"\nLog {i}:\n"
                f"Text: {log['log_text']}\n"
                f"Protocol: {log.get('protocols', 'unknown')}\n"
                f"Severity: {log.get('severity', 'unknown')}\n"
            )

        return f"""{self.base_prompt}

{context}

Troubleshooting Request:
{question}

Provide:
- Root cause analysis
- Step-by-step diagnosis
- Solution recommendations
- Prevention measures

Answer:
"""

    # -------------------------------------------------
    # MODE-BASED PROMPT SELECTOR
    # -------------------------------------------------
    def create_prompt(self, question: str, logs: List[Dict], mode: str = 'analysis') -> str:
        """
        Create prompt based on mode
        
        Args:
            question: User's question
            logs: Retrieved log entries
            mode: One of ['analysis', 'security', 'summary', 'troubleshooting']
        
        Returns:
            Formatted prompt string
        """
        mode = mode.lower()
        
        if mode == 'security':
            return self.create_security_prompt(logs)
        elif mode == 'summary':
            return self.create_summary_prompt(logs)
        elif mode == 'troubleshooting':
            return self.create_troubleshooting_prompt(question, logs)
        else:  # default to analysis
            return self.create_analysis_prompt(question, logs)

    # -------------------------------------------------
    # CONVERSATIONAL CONTEXT
    # -------------------------------------------------
    def add_conversation_context(self, prompt: str, history: List[Dict]) -> str:
        """
        Add conversation history to prompt
        
        Args:
            prompt: Base prompt
            history: List of previous exchanges [{'role': 'user/assistant', 'content': '...'}]
        
        Returns:
            Enhanced prompt with context
        """
        if not history:
            return prompt
        
        context = "\n=== CONVERSATION HISTORY ===\n"
        for exchange in history[-3:]:  # Last 3 exchanges
            role = exchange['role'].upper()
            content = exchange['content'][:200]  # Truncate long messages
            context += f"{role}: {content}\n"
        
        return f"{context}\n{prompt}"

    # -------------------------------------------------
    # SYSTEM PROMPT TEMPLATES
    # -------------------------------------------------
    @staticmethod
    def get_system_prompt(mode: str = 'analysis') -> str:
        """Get system-level prompt based on mode"""
        prompts = {
            'analysis': """You are an expert ICS security analyst with 15+ years of experience in SCADA systems, 
OT networks, and industrial protocols (Modbus, DNP3, BACnet, SNMP). You provide detailed, 
actionable analysis while prioritizing safety and system availability.""",
            
            'summary': """You are a technical summarizer specializing in industrial control systems. 
You distill complex log data into clear, concise summaries highlighting critical events, 
patterns, and required actions.""",
            
            'security': """You are a cybersecurity expert specializing in Industrial Control Systems 
and critical infrastructure protection. You identify threats, vulnerabilities, and attack 
indicators with a focus on preventing operational disruption.""",
            
            'troubleshooting': """You are an ICS troubleshooting expert with deep knowledge of 
industrial protocols, SCADA architectures, and common failure modes. You provide systematic 
root cause analysis and practical solutions."""
        }
        return prompts.get(mode, prompts['analysis'])

    # -------------------------------------------------
    # ENHANCED CONTEXT FORMATTING
    # -------------------------------------------------
    @staticmethod
    def format_logs_compact(logs: List[Dict]) -> str:
        """Format logs in compact format for context"""
        formatted = "=== RETRIEVED LOGS ===\n"
        for i, log in enumerate(logs, 1):
            formatted += f"\n[{i}] {log.get('severity', 'INFO').upper()}: "
            formatted += f"{log['log_text'][:150]}"  # Truncate long logs
            formatted += f" | Protocol: {log.get('protocols', 'unknown')}"
            formatted += f" | Score: {log['similarity_score']:.2f}\n"
        return formatted

    # -------------------------------------------------
    # PROMPT OPTIMIZATION
    # -------------------------------------------------
    def optimize_for_model(self, prompt: str, model_name: str) -> str:
        """
        Optimize prompt format for specific models
        
        Args:
            prompt: Base prompt
            model_name: Ollama model name (e.g., 'llama3:8b-instruct-q4_0')
        
        Returns:
            Optimized prompt
        """
        # For instruct models, use clear instruction format
        if 'instruct' in model_name.lower():
            return f"<|start_header_id|>system<|end_header_id|>\n\n{self.base_prompt}\n\n<|start_header_id|>user<|end_header_id|>\n\n{prompt}\n\n<|start_header_id|>assistant<|end_header_id|>\n\n"
        
        # For base models, use simple format
        return prompt

    # -------------------------------------------------
    # VALIDATION
    # -------------------------------------------------
    @staticmethod
    def validate_logs(logs: List[Dict]) -> bool:
        """Validate log format"""
        if not logs:
            return False
        
        required_fields = ['log_text', 'similarity_score']
        return all(
            all(field in log for field in required_fields)
            for log in logs
        )

    # -------------------------------------------------
    # HELPER: EXTRACT KEY TERMS
    # -------------------------------------------------
    @staticmethod
    def extract_key_terms(question: str) -> List[str]:
        """Extract key terms from question for emphasis"""
        # Common ICS/security terms
        key_terms = [
            'modbus', 'dnp3', 'bacnet', 'snmp', 'scada',
            'authentication', 'failure', 'error', 'critical',
            'unauthorized', 'timeout', 'connection', 'security'
        ]
        
        question_lower = question.lower()
        found_terms = [term for term in key_terms if term in question_lower]
        return found_terms