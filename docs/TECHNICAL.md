# Technical Documentation

Complete technical architecture and implementation details for ICS-LogQueryGPT.

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Core Components](#core-components)
- [RAG Pipeline](#rag-pipeline)
- [Authentication System](#authentication-system)
- [Alert System](#alert-system)
- [Benchmark & Evaluation](#benchmark--evaluation)
- [Performance](#performance)

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    UI Layer (Streamlit)                        │
│                                                                │
│  Login  │  Home  │  Query Logs  │  Analytics  │  Export       │
│  Admin Dashboard  │  Benchmark (admin only)                   │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                  Authentication Layer                          │
│  SQLite users.db  │  bcrypt hashing  │  Session tokens        │
│  Role-based access: admin / analyst / viewer                  │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    RAG Pipeline                                │
│                                                                │
│  [1] BERT Embedding → 768-dim vector                          │
│  [2] FAISS Vector Search → top-K logs                         │
│  [3] Context Assembly → prompt construction                   │
│  [4] Groq LLM (llama-3.1-8b-instant) → answer                │
│  [4b] Gemini Flash fallback (if Groq fails)                   │
│  [5] Critical Keyword Scan → email alert if triggered         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    Storage Layer                               │
│  HDFS_index.faiss  │  BGL_index.faiss  │  users.db            │
│  sessions.db       │  .cache/ (MiniLM) │  .env (API keys)     │
└──────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Primary LLM** | Groq — llama-3.1-8b-instant | Fast AI response generation |
| **Fallback LLM** | Google Gemini Flash | Automatic fallback reliability |
| **LLM Framework** | LangChain | LLM abstraction and chaining |
| **Dataset Embeddings** | BERT (bert-base-uncased) | 768-dim semantic vectors |
| **Upload Embeddings** | MiniLM (all-MiniLM-L6-v2) | Fast file indexing (5–8s) |
| **Vector Search** | FAISS (IndexFlatIP) | Sub-millisecond similarity search |
| **Web Framework** | Streamlit | UI and routing |
| **Auth DB** | SQLite + bcrypt | User/session management |
| **Alert Email** | Gmail SMTP SSL | Instant email on critical detection |
| **Charts** | Plotly | Interactive analytics visualizations |
| **Language** | Python 3.8+ | Application logic |

### Key Libraries

```
streamlit>=1.28.0
langchain-groq
langchain-google-genai
langchain-core
sentence-transformers
faiss-cpu
transformers
torch
numpy
pandas
bcrypt
python-dotenv
plotly
```

---

## Core Components

### 1. BERT Embedder

**File:** `src/rag_system/integrated_rag_ollama.py`

Converts log text and queries into 768-dimensional vectors using `bert-base-uncased`. The [CLS] token embedding is extracted and L2-normalized for cosine similarity search via FAISS IndexFlatIP.

```python
# Embedding process
inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
outputs = model(**inputs)
embedding = outputs.last_hidden_state[:, 0, :].numpy()  # CLS token
return embedding / np.linalg.norm(embedding)             # Normalize
```

**Cache:** `D:/Projects/log_query_gpt/.cache/huggingface`

### 2. MiniLM Embedder (for uploaded files)

**File:** `src/ui/pages/1_Query_Logs.py`

Uses `all-MiniLM-L6-v2` for fast indexing of user-uploaded files. Embedding time is 5–8 seconds for a typical CSV file compared to ~40 seconds with BERT.

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts, show_progress_bar=True)
```

**Cache:** `D:/Projects/log_query_gpt/.cache/sentence_transformers`

### 3. FAISS Vector Search

**Index type:** `IndexFlatIP` (Inner Product / cosine similarity after normalization)

Two indexes are pre-built and stored on disk:
- `data/vector_db/HDFS_index.faiss` — 2,000 HDFS log vectors
- `data/vector_db/BGL_index.faiss` — 2,000 BGL log vectors

Search returns top-K results with similarity scores. Default K=5.

### 4. Groq + Gemini LLM

**File:** `src/rag_system/basic_rag_ollama.py`

Uses LangChain with `ChatGroq` as primary and `ChatGoogleGenerativeAI` as fallback.

```python
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

primary_llm   = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=...)
fallback_llm  = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=...)
```

If the Groq API call fails (rate limit, timeout, etc.), the system silently falls back to Gemini Flash.

### 5. Query Modes

| Mode | Top-K Logs | Temperature | Use Case |
|------|-----------|-------------|----------|
| Fast | 3 | 0.3 | Quick overview |
| Detailed | 5 | 0.5 | Investigation |
| Deep Analysis | 8 | 0.7 | Full audit |

---

## RAG Pipeline

Full query flow from user input to response:

```
1. User submits query text
2. Query embedded with BERT → 768-dim vector
3. FAISS search on selected dataset (HDFS/BGL/uploaded)
4. Top-K logs retrieved with similarity scores
5. Prompt assembled:
   - System instruction (security analyst persona)
   - Retrieved log entries with metadata
   - User query
6. Groq API called → streamed response
7. Response scanned for critical keywords
8. If critical: red banner shown + email sent
9. Result stored in session state (query_history, current_results)
```

---

## Authentication System

**Files:** `src/ui/auth/user_manager.py`, `src/ui/auth/session.py`

### Users Database (`data/users.db`)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,       -- bcrypt
    role TEXT NOT NULL,                -- admin / analyst / viewer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    active BOOLEAN DEFAULT 1
)
```

### Sessions Database (`data/sessions.db`)

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_token TEXT UNIQUE NOT NULL, -- UUID4
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    user_role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,      -- 30 min timeout
    active BOOLEAN DEFAULT 1
)
```

### Role Permissions

| Role | Query Logs | Analytics | Export | Admin Dashboard | Benchmark |
|------|-----------|-----------|--------|----------------|-----------|
| admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| analyst | ✅ | ✅ | ✅ | ❌ | ❌ |
| viewer | ✅ | ✅ | ✅ | ❌ | ❌ |

### Login Flow

```
Login page → credentials checked →
  admin role → redirect to Admin Dashboard
  other role → redirect to Home page
```

---

## Alert System

**File:** `src/ui/utils/alert_system.py`

### Critical Keywords

The system scans every AI response for:
```
brute force, attack, intrusion, unauthorized, authentication failure,
failed login, blocked, critical, malware, exploit, suspicious,
anomaly, threat, breach, compromised, escalation, privilege escalation,
root access, fatal, kernel panic, memory corruption, hardware failure,
node failure, excessive, flood, denial of service, dos attack
```

### Severity Classification

- **CRITICAL** — attack, brute force, intrusion, unauthorized, malware, exploit, breach, fatal, kernel panic
- **WARNING** — all other keyword matches

### Email Format

Sends an HTML email via Gmail SMTP SSL (port 465) with:
- Severity badge (red/yellow)
- Original query that triggered the alert
- AI answer (first 800 characters)
- Metadata: dataset, response time, triggering user, timestamp

### Configuration (.env)

```
ALERT_EMAIL=sender@gmail.com
ALERT_EMAIL_PASSWORD=your_16char_app_password
ALERT_RECIPIENT=recipient@gmail.com
```

---

## Benchmark & Evaluation

**File:** `src/ui/pages/6_Benchmark.py` (admin only)

### Test Set

8 questions (4 HDFS + 4 BGL) with detailed reference answers. Covers authentication failures, brute force, connection errors, hardware failures, fatal errors, and system crashes.

### Generation Metrics

| Metric | What It Measures |
|--------|-----------------|
| **BLEU** | N-gram word overlap between AI answer and reference |
| **ROUGE-1** | Unigram recall — individual word coverage |
| **ROUGE-2** | Bigram recall — two-word phrase coverage |
| **ROUGE-L** | Longest common subsequence match |

### Retrieval Metrics

| Metric | What It Measures |
|--------|-----------------|
| **Precision@5** | Fraction of top-5 retrieved logs that are relevant |
| **Recall@5** | Fraction of all relevant logs found in top-5 |
| **MRR** | Mean Reciprocal Rank — position of first relevant log |

### Results

| Metric | Score |
|--------|-------|
| Recall@5 | 1.000 (perfect) |
| MRR | 1.000 (perfect) |
| Precision@5 | 0.400 |
| ROUGE-1 | ~0.092 |
| BLEU | ~0.022 |
| Avg Time | ~7.4s |

Low BLEU/ROUGE scores are expected in RAG systems where AI answers paraphrase rather than reproduce reference text verbatim. Perfect Recall@5 and MRR confirm the retrieval pipeline works correctly.

---

## Performance

| Operation | Time |
|-----------|------|
| BERT embedding (single query) | ~200ms |
| FAISS search (2,000 vectors) | <1ms |
| Groq LLM generation | 1–3s |
| Gemini Flash fallback | 2–5s |
| MiniLM file indexing (~1,000 logs) | 5–8s |
| Full end-to-end query | 2–8s |

---

**Version:** 1.0.0 | **Last Updated:** March 2026
