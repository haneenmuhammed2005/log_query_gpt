# 🏗️ Technical Documentation

Complete technical architecture and implementation details for ICS-LogQueryGPT.

---

## 📋 Table of Contents

- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Core Components](#-core-components)
- [Data Pipeline](#-data-pipeline)
- [RAG Implementation](#-rag-implementation)
- [Performance Optimization](#-performance-optimization)
- [API Reference](#-api-reference)

---

## 🏛️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface Layer                        │
│                     (Streamlit Web App)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ Protocol │  │ Severity │  │ Analysis │  │ Conversation │   │
│  │ Filters  │  │ Filters  │  │   Mode   │  │   History    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Application Logic Layer                       │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Conversational RAG System                       │   │
│  │  • Query Processing & Expansion                         │   │
│  │  • Context Management                                   │   │
│  │  • Response Generation                                  │   │
│  │  • Conversation Memory                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Data Processing Layer                      │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │   Protocol   │  │   Enhanced   │  │  Vector Search   │     │
│  │  Detection   │  │  Embeddings  │  │     (FAISS)      │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                         AI/ML Layer                              │
│                                                                   │
│  ┌──────────────────────┐       ┌──────────────────────┐       │
│  │   BERT Encoder       │       │   Llama 3.1 LLM      │       │
│  │  (bert-base-uncased) │       │     (via Ollama)     │       │
│  │   768-dim vectors    │       │   8B / 70B models    │       │
│  └──────────────────────┘       └──────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                        Storage Layer                             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │   Raw Logs   │  │  Processed   │  │    Embeddings    │     │
│  │     CSV      │  │     CSV      │  │       NPY        │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User Query
    ↓
[1] Query Preprocessing
    • Tokenization
    • Protocol detection
    • Query expansion
    ↓
[2] Embedding Generation (BERT)
    • Convert query to 768-dim vector
    • Normalize vector
    ↓
[3] Vector Search (FAISS)
    • Similarity search
    • Apply filters (protocol, severity)
    • Rank results
    ↓
[4] Context Assembly
    • Retrieve top-k logs
    • Add metadata (protocol, severity, timestamp)
    • Format for LLM
    ↓
[5] Prompt Construction
    • Select analysis mode template
    • Insert retrieved logs
    • Add conversation history
    ↓
[6] LLM Generation (Llama 3.1)
    • Generate response
    • Cite sources
    • Provide insights
    ↓
[7] Post-processing
    • Format response
    • Update conversation history
    • Log metrics
    ↓
Response to User
```

---

## 🛠️ Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **LLM** | Llama 3.1 | 8B/70B | Natural language generation |
| **LLM Serving** | Ollama | Latest | Local LLM inference |
| **Embeddings** | BERT | base-uncased | Semantic text encoding |
| **Vector DB** | FAISS | 1.7.4 | Fast similarity search |
| **Web Framework** | Streamlit | 1.28+ | User interface |
| **ML Framework** | PyTorch | 2.0+ | Deep learning backend |
| **Language** | Python | 3.8+ | Application logic |

### Key Libraries

```python
# requirements.txt
streamlit>=1.28.0          # Web UI
ollama>=0.1.0              # Ollama client
sentence-transformers>=2.2.0  # BERT embeddings
faiss-cpu>=1.7.4           # Vector search
numpy>=1.24.0              # Numerical operations
pandas>=2.0.0              # Data manipulation
torch>=2.0.0               # PyTorch
transformers>=4.30.0       # HuggingFace models
```

---

## 🧩 Core Components

### 1. Protocol Detector

**File:** `src/preprocessing/protocol_detector.py`

**Purpose:** Detect ICS/SCADA protocols in log entries

**Supported Protocols:**
- Modbus TCP/RTU
- DNP3
- SNMP
- SSH
- HTTP/HTTPS
- FTP
- Telnet
- BACnet

**Algorithm:**
```python
class ProtocolDetector:
    def detect_protocol(self, log_text: str) -> List[str]:
        """
        Two-pass detection:
        1. Explicit protocol names (high priority)
        2. Protocol-specific patterns (if no explicit match)
        """
        # Pass 1: Look for explicit mentions
        for protocol, pattern in explicit_protocols.items():
            if re.search(pattern, log_text):
                return [protocol]
        
        # Pass 2: Pattern-based detection
        detected = []
        for protocol, patterns in protocol_patterns.items():
            if any(re.search(p, log_text) for p in patterns):
                detected.append(protocol)
        
        return detected if detected else ['unknown']
```

**Key Features:**
- Word boundary matching to avoid false positives
- Priority-based pattern matching
- Severity level detection
- Extensible pattern system

---

### 2. Log Embedder

**File:** `src/embeddings/log_embedder.py`

**Purpose:** Convert log text to 768-dimensional vectors

**Model:** `bert-base-uncased` from HuggingFace

**Architecture:**
```python
class LogEmbedder:
    def __init__(self):
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def embed_single_log(self, text: str) -> np.ndarray:
        """
        Process:
        1. Tokenize text (max 512 tokens)
        2. Pass through BERT encoder
        3. Extract [CLS] token embedding
        4. Normalize to unit length
        """
        inputs = self.tokenizer(text, return_tensors='pt', 
                               truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].numpy()
        return embedding / np.linalg.norm(embedding)
    
    def embed_batch(self, texts: List[str], batch_size: int = 32):
        """Batch processing for efficiency"""
        embeddings = []
        for i in tqdm(range(0, len(texts), batch_size)):
            batch = texts[i:i+batch_size]
            batch_emb = [self.embed_single_log(t) for t in batch]
            embeddings.extend(batch_emb)
        return np.vstack(embeddings)
```

**Performance:**
- CPU: ~120 logs/second
- GPU: ~500+ logs/second
- Memory: ~2GB for model

---

### 3. Vector Search Engine

**File:** `src/vector_db/optimized_search.py`

**Purpose:** Fast similarity search with filtering

**Index Types:**

1. **Flat Index** (< 10K vectors)
   - Exact search
   - No compression
   - Sub-millisecond search

2. **IVF Index** (10K - 1M vectors)
   - Approximate search
   - Clustering-based
   - Configurable accuracy/speed tradeoff

**Implementation:**
```python
class OptimizedVectorDB:
    def build_index(self, embeddings: np.ndarray, metadata: pd.DataFrame):
        """
        Auto-select index type based on size
        """
        n_vectors = len(embeddings)
        
        if n_vectors < 10000:
            # Flat index for small datasets
            self.index = faiss.IndexFlatIP(768)
        else:
            # IVF index for larger datasets
            n_clusters = int(np.sqrt(n_vectors))
            quantizer = faiss.IndexFlatIP(768)
            self.index = faiss.IndexIVFFlat(quantizer, 768, n_clusters)
            self.index.train(embeddings)
        
        self.index.add(embeddings)
    
    def search_with_filter(self, query: np.ndarray, k: int, 
                          protocol_filter: str = None,
                          severity_filter: str = None):
        """
        1. Perform vector search (retrieve top-k*3)
        2. Apply metadata filters
        3. Return top-k filtered results
        """
        # Over-retrieve to account for filtering
        scores, indices = self.index.search(query, k * 3)
        
        # Apply filters
        results = []
        for idx, score in zip(indices[0], scores[0]):
            log = self.metadata.iloc[idx]
            
            if protocol_filter and protocol_filter not in log['protocols']:
                continue
            if severity_filter and log['severity'] != severity_filter:
                continue
            
            results.append({
                'log_text': log['cleaned'],
                'protocols': log['protocols'],
                'severity': log['severity'],
                'similarity_score': float(score)
            })
            
            if len(results) >= k:
                break
        
        return results
```

**Performance Characteristics:**
- **Search Time**: <100ms for 2000 vectors
- **Memory**: ~6MB per 1000 vectors (768-dim)
- **Scalability**: Handles millions of vectors with IVF

---

### 4. RAG System

**File:** `src/rag_system/conversational_rag_ollama.py`

**Purpose:** Context-aware response generation

**Architecture:**
```python
class ConversationalRAGOllama:
    def __init__(self, model_name: str = 'llama3.1:8b'):
        self.model = model_name
        self.conversation_history = []
        self.embedder = LogEmbedder()
        self.vector_db = OptimizedVectorDB()
    
    def generate_with_context(self, query: str, 
                             retrieved_logs: List[Dict],
                             mode: str = 'analysis'):
        """
        RAG Pipeline:
        1. Expand query (add context from conversation)
        2. Construct prompt using template
        3. Generate response via Ollama
        4. Update conversation history
        """
        # Query expansion
        expanded_query = self._expand_query(query)
        
        # Select prompt template
        template = self.templates[mode]
        
        # Construct prompt
        prompt = template.format(
            query=expanded_query,
            logs=self._format_logs(retrieved_logs),
            history=self._format_history()
        )
        
        # Generate
        response = self._call_ollama(prompt)
        
        # Update history
        self.conversation_history.append({
            'query': query,
            'response': response,
            'logs_used': len(retrieved_logs)
        })
        
        return response
```

**Prompt Templates:**

1. **Analysis Mode:**
```python
"""
You are an expert ICS/SCADA log analyzer.

Retrieved Logs:
{logs}

User Question: {query}

Provide a detailed analysis:
1. What happened?
2. Which systems were affected?
3. What was the impact?
4. What should be done?

Cite specific logs (Log 1, Log 2, etc.).
"""
```

2. **Security Mode:**
```python
"""
You are a cybersecurity expert specializing in ICS/SCADA systems.

Retrieved Logs:
{logs}

User Question: {query}

Security Analysis:
1. Threat Assessment
2. Attack Vectors
3. Affected Assets
4. Recommended Actions

Focus on security implications.
"""
```

**Query Expansion:**
```python
def _expand_query(self, query: str) -> str:
    """
    Add context from recent conversation history
    """
    if not self.conversation_history:
        return query
    
    # Get last 2 exchanges
    recent = self.conversation_history[-2:]
    context = " ".join([f"Previous: {h['query']}" for h in recent])
    
    return f"{context} Current: {query}"
```

---

## 📊 Data Pipeline

### Pipeline Stages

```
Raw Logs
    ↓
[1] Download & Extract
    • fetch_data.py
    • Extract from archives
    ↓
[2] Preprocessing
    • Clean text
    • Remove duplicates
    • Normalize timestamps
    ↓
[3] Protocol Detection
    • Identify ICS protocols
    • Detect severity levels
    • Add metadata
    ↓
[4] Embedding Generation
    • Tokenize with BERT
    • Generate 768-dim vectors
    • Normalize embeddings
    ↓
[5] Index Building
    • Select index type
    • Build FAISS index
    • Save to disk
    ↓
Ready for Search
```

### Data Format

**Raw Log Entry:**
```
2024-01-15 08:23:45,INFO,Device 5 Modbus read failure on coil 100
```

**After Preprocessing:**
```python
{
    'original': '2024-01-15 08:23:45,INFO,Device 5 Modbus read failure on coil 100',
    'cleaned': 'device 5 modbus read failure on coil 100',
    'timestamp': '2024-01-15 08:23:45',
    'protocols': 'modbus',
    'severity': 'high',
    'embedding': [0.023, -0.145, ...] # 768 dimensions
}
```

---

## ⚡ Performance Optimization

### Optimization Strategies

**1. Batch Processing**
```python
# Process embeddings in batches
for i in range(0, len(logs), BATCH_SIZE):
    batch = logs[i:i+BATCH_SIZE]
    embeddings = embedder.embed_batch(batch)
```

**2. GPU Acceleration**
```python
# Automatically use GPU if available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = model.to(device)
```

**3. Caching**
```python
@lru_cache(maxsize=1000)
def embed_query(query: str):
    return embedder.embed_single_log(query)
```

**4. Index Optimization**
```python
# Use IVF for large datasets
if n_vectors > 10000:
    n_clusters = int(np.sqrt(n_vectors))
    index = faiss.IndexIVFFlat(quantizer, dim, n_clusters)
```

### Performance Benchmarks

| Operation | Time | Throughput |
|-----------|------|------------|
| **Embedding (single)** | 4ms | 250/sec |
| **Embedding (batch)** | - | 120/sec |
| **Vector Search** | <1ms | 1000+/sec |
| **LLM Generation (8B)** | 3-8s | 40-100 tokens/s |
| **LLM Generation (70B)** | 15-30s | 10-30 tokens/s |
| **End-to-End Query** | 4-10s | - |

---

## 📡 API Reference

### LogEmbedder

```python
from embeddings.log_embedder import LogEmbedder

embedder = LogEmbedder()

# Single embedding
embedding = embedder.embed_single_log("authentication failed")
# Returns: np.ndarray shape (768,)

# Batch embedding
embeddings = embedder.embed_batch(["log 1", "log 2"], batch_size=32)
# Returns: np.ndarray shape (n, 768)
```

### ProtocolDetector

```python
from preprocessing.protocol_detector import ProtocolDetector

detector = ProtocolDetector()

# Detect protocols
protocols = detector.detect_protocol("modbus read failed")
# Returns: ['modbus']

# Detect severity
severity = detector.detect_severity("critical authentication failure")
# Returns: 'critical'
```

### OptimizedVectorDB

```python
from vector_db.optimized_search import OptimizedVectorDB

db = OptimizedVectorDB()

# Build index
db.build_index(embeddings, metadata_df)

# Search
results = db.search_with_filter(
    query_embedding,
    k=5,
    protocol_filter='modbus',
    severity_filter='high'
)
# Returns: List[Dict] with similarity scores
```

### ConversationalRAGOllama

```python
from rag_system.conversational_rag_ollama import ConversationalRAGOllama

rag = ConversationalRAGOllama(model_name='llama3.1:8b')

# Start conversation
rag.start_conversation()

# Generate response
result = rag.generate_with_context(
    query="What authentication issues occurred?",
    retrieved_logs=logs,
    mode='security'
)

# Export conversation
rag.export_conversation('conversation.json')
```

---

## 🔐 Security Considerations

### Data Privacy

- **No External API Calls**: All processing is local
- **No Telemetry**: No usage data sent anywhere
- **Encrypted Storage**: Option to encrypt embeddings at rest

### Access Control

```python
# Example: Add basic authentication
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    credentials,
    cookie_name='ics_logquery',
    key='some_signature_key',
    cookie_expiry_days=30
)

name, authentication_status = authenticator.login('Login', 'main')

if authentication_status:
    # Show application
    run_app()
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

---

## 📈 Scalability

### Handling Large Datasets

**Current Capacity:**
- 2,000 logs: <100ms search
- 100,000 logs: <500ms search
- 1M+ logs: <2s search (with IVF index)

**Scaling Strategies:**

1. **Horizontal Scaling**: Use FAISS distributed indexing
2. **Vertical Scaling**: Add more RAM/CPU
3. **Partitioning**: Split by time/protocol
4. **Streaming**: Process logs in real-time

---

## 🧪 Testing

### Test Suite

```bash
python tests/test_complete_system.py
```

**Test Coverage:**
- Protocol detection accuracy
- Embedding generation quality
- Vector search correctness
- RAG system functionality
- Conversation memory
- Data integrity

---

## 📚 References

- [Llama 3.1 Paper](https://ai.meta.com/research/publications/llama-3-herd-of-models/)
- [BERT Paper](https://arxiv.org/abs/1810.04805)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [RAG Overview](https://arxiv.org/abs/2005.11401)

---

**Version**: 1.0.0  
**Last Updated**: January 21, 2026  
**Maintained by**: ICS-LogQueryGPT Team