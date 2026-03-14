# ICS-LogQueryGPT

**AI-Powered Log Analysis for Industrial Control Systems**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/AI-Groq%20+%20Gemini%20Flash-green.svg)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Query your ICS/SCADA security logs using natural language. Powered by BERT semantic embeddings, FAISS vector search, and Groq + Gemini Flash AI for 1–3 second responses.

---

## Features

- **Natural Language Queries** — Ask questions in plain English, no query syntax required
- **BERT + FAISS Retrieval** — 4,000+ log vectors across HDFS and BGL datasets with semantic search
- **Groq + Gemini Flash AI** — 1–3 second responses with automatic fallback for reliability
- **Upload Any Log File** — CSV or TXT files indexed instantly using MiniLM embeddings
- **Critical Alert System** — Auto-detects threats and sends instant email alerts
- **Role-Based Access** — Admin, Analyst, and Viewer roles with session management
- **Admin Dashboard** — User management, activity log, create users, benchmark access
- **Benchmark Metrics** — BLEU, ROUGE, Precision@5, Recall@5, MRR evaluation suite
- **Export Center** — CSV, JSON, Markdown export with templates and history tracking
- **Analytics Dashboard** — Real session-based charts and query history visualization

---

## Quick Start

### Prerequisites

- Python 3.8+
- 8GB RAM minimum
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Google API key (free at [aistudio.google.com](https://aistudio.google.com))

### Installation

```bash
# 1. Clone repository
git clone https://github.com/haneenmuhammed2005/ICS-LogQueryGPT.git
cd ICS-LogQueryGPT

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create a .env file in the project root:
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
ALERT_EMAIL=your_gmail@gmail.com
ALERT_EMAIL_PASSWORD=your_gmail_app_password
ALERT_RECIPIENT=recipient@gmail.com

# 5. Build FAISS indexes (first time only)
python build_bgl_index.py

# 6. Launch application
streamlit run src/ui/app.py
```

**Access at:** http://localhost:8501

### Default Login

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |

Any new sign-up gets the `analyst` role automatically.

---

## Usage

### Example Queries

**HDFS Dataset:**
- "Show all failed login attempts"
- "Are there any brute force attacks?"
- "Which IP addresses have the most failed connections?"
- "Show me all blocked connections"

**BGL Dataset:**
- "Are there any hardware failures in the logs?"
- "Show all fatal errors"
- "What caused the most system crashes?"
- "Are there any memory failures?"

**Upload Your Own File:**
- Upload any CSV or TXT log file
- Query it instantly with the same natural language interface

### Query Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **Fast** | Quick overview, 1–3s response | General queries |
| **Detailed** | Deep analysis, 3–6s response | Investigation |
| **Deep Analysis** | Comprehensive, 5–10s response | Full audit |

---

## Architecture

```
User Query (Natural Language)
        ↓
[1] BERT Embedding (768-dim vector)
        ↓
[2] FAISS Vector Search (top-K retrieval)
        ↓
[3] Context Assembly (retrieved logs + metadata)
        ↓
[4] Groq LLM Generation (llama-3.1-8b-instant)
        ↓  [fallback if Groq fails]
[4b] Gemini Flash Generation
        ↓
[5] Critical Keyword Detection → Email Alert
        ↓
Response + Alert Banner (if triggered)
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Primary LLM** | Groq — llama-3.1-8b-instant |
| **Fallback LLM** | Google Gemini Flash |
| **Embeddings (dataset)** | BERT (bert-base-uncased, 768-dim) |
| **Embeddings (upload)** | MiniLM (all-MiniLM-L6-v2) |
| **Vector Search** | FAISS (IndexFlatIP) |
| **Web Framework** | Streamlit |
| **Authentication** | SQLite + bcrypt |
| **Alert Email** | Gmail SMTP (SSL) |
| **Language** | Python 3.8+ |

---

## Project Structure

```
ICS-LogQueryGPT/
├── src/
│   ├── ui/
│   │   ├── app.py                          # Home page
│   │   ├── pages/
│   │   │   ├── 0_Login.py                  # Login / Sign Up
│   │   │   ├── 1_Query_Logs.py             # Main query interface
│   │   │   ├── 2_Analytics.py              # Session analytics
│   │   │   ├── 3_Export.py                 # Export center
│   │   │   ├── 5_Admin.py                  # Admin dashboard
│   │   │   └── 6_Benchmark.py              # Metrics evaluation (admin only)
│   │   ├── auth/
│   │   │   ├── user_manager.py             # User CRUD + bcrypt
│   │   │   └── session.py                  # Session management
│   │   └── utils/
│   │       └── alert_system.py             # Critical alert + email
│   ├── rag_system/
│   │   ├── basic_rag_ollama.py             # Groq + Gemini LLM
│   │   └── integrated_rag_ollama.py        # Full RAG pipeline
│   └── evaluation/
│       ├── metrics.py                      # Precision@K, Recall@K, MRR, NDCG
│       └── benchmark.py                    # Performance benchmarking
├── data/
│   └── vector_db/
│       ├── HDFS_index.faiss                # HDFS FAISS index
│       ├── HDFS_metadata.pkl               # HDFS metadata
│       ├── BGL_index.faiss                 # BGL FAISS index
│       └── BGL_metadata.pkl                # BGL metadata
├── build_bgl_index.py                      # Run once to build BGL index
├── auth_logs_1000.csv                      # Sample log file for testing
├── .env                                    # API keys (not in git)
├── requirements.txt
└── README.md
```

---

## Performance

### Benchmark Results

| Metric | Score | Interpretation |
|--------|-------|----------------|
| **Recall@5** | **1.000** | Perfect — all relevant logs found |
| **MRR** | **1.000** | Perfect — relevant log always ranked #1 |
| **Precision@5** | 0.400 | 2 of top-5 retrieved logs are relevant |
| **ROUGE-1** | 0.092 | Consistent with open-domain RAG systems |
| **BLEU** | 0.022 | Normal for paraphrasing-based generation |
| **Avg Response Time** | ~7.4s | Acceptable for BERT + Groq RAG pipeline |

> Recall@5 = 1.0 and MRR = 1.0 confirm the BERT + FAISS retrieval system is perfect — every relevant log entry is retrieved in the top 5 results for every test query.

### System Requirements

| | Minimum | Recommended |
|--|---------|-------------|
| **CPU** | 4 cores | 8+ cores |
| **RAM** | 8GB | 16GB |
| **Storage** | 5GB | 10GB |
| **Internet** | Required (Groq API) | Required |

---

## Documentation

- [User Guide](docs/USER_GUIDE.md) — Complete usage instructions
- [Deployment Guide](docs/DEPLOYMENT.md) — Local and Docker deployment
- [Technical Documentation](docs/TECHNICAL.md) — Architecture and internals
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues and solutions
- [Quick Reference](docs/QUICK_REFERENCE.md) — Cheat sheet

---

## Alert System

When a query response contains critical keywords (attack, brute force, unauthorized, blocked, fatal, critical, etc.), the system automatically:

1. Shows a red/yellow alert banner in the UI
2. Sends an HTML email to the configured recipient instantly

To configure alerts, set these in your `.env` file:
```
ALERT_EMAIL=sender@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
ALERT_RECIPIENT=recipient@gmail.com
```

---

## License

This project is licensed under the MIT License.

---

**Built with Space Grotesk, BERT, FAISS, Groq, and Streamlit**

*Version 1.0.0 — Last Updated: March 2026*
