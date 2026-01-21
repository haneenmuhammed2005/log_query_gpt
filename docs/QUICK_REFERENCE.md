# ⚡ Quick Reference Guide

One-page cheat sheet for ICS-LogQueryGPT.

---

## 🚀 Quick Start Commands

```bash
# Setup (first time)
git clone https://github.com/haneenmuhammed2005/ICS-LogQueryGPT.git
cd ICS-LogQueryGPT
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3.1:8b

# Prepare data
python src/preprocessing/download_data.py
python src/preprocessing/process_all_data.py
python src/embeddings/enhanced_embedder.py

# Launch
ollama serve &  # Start Ollama
streamlit run src/ui/enhanced_app_ollama.py
```

---

## 💡 Example Queries

| Query Type | Example |
|------------|---------|
| **Security** | "Show authentication failures" |
| **Protocol** | "Find Modbus communication errors" |
| **Troubleshooting** | "Why did device 5 fail?" |
| **Analysis** | "What caused the system outage?" |
| **Follow-up** | "Which IP was it?" (after previous query) |

---

## ⚙️ Common Settings

| Setting | Recommended | Fast | Accurate |
|---------|-------------|------|----------|
| **Model** | llama3.1:8b | 8b | 70b |
| **Num Logs** | 5 | 3 | 10 |
| **Temperature** | 0.7 | 0.3 | 0.5 |
| **Min Similarity** | 0.3 | 0.5 | 0.2 |

---

## 🔧 Troubleshooting Commands

```bash
# Check Ollama
curl http://localhost:11434/api/tags
ollama list

# Test system
python tests/test_complete_system.py

# Restart services
pkill -f ollama && ollama serve &
pkill -f streamlit

# Rebuild data
rm -rf data/embeddings/*
python src/embeddings/enhanced_embedder.py
```

---

## 📊 Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| Search | <100ms | 50-100ms |
| Generation (8B) | <10s | 3-8s |
| Embedding | >100/s | 120/s |
| Accuracy | >90% | 95%+ |

---

## 🔑 Key Files

```
ICS-LogQueryGPT/
├── src/ui/enhanced_app_ollama.py       # Main UI
├── src/rag_system/conversational_rag_ollama.py  # RAG logic
├── src/embeddings/log_embedder.py      # BERT embeddings
├── src/vector_db/optimized_search.py   # Vector search
├── tests/test_complete_system.py       # Test suite
└── requirements.txt                     # Dependencies
```

---

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| **Ollama not found** | `ollama serve` |
| **Model missing** | `ollama pull llama3.1:8b` |
| **Slow responses** | Use 8B model, reduce logs |
| **File not found** | Run data pipeline scripts |
| **Import errors** | `pip install -r requirements.txt` |

**Full docs**: `docs/TROUBLESHOOTING.md`

---

## 🎯 Success Checklist

- [ ] Ollama running (`curl http://localhost:11434/api/tags`)
- [ ] Model downloaded (`ollama list`)
- [ ] Data processed (`ls data/embeddings/`)
- [ ] Tests pass (`python tests/test_complete_system.py`)
- [ ] UI accessible (http://localhost:8501)

---

**Version**: 1.0.0 | [Full Documentation](docs/)