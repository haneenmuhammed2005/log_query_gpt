# Quick Reference

One-page cheat sheet for ICS-LogQueryGPT.

---

## Launch

```bash
# Activate environment
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Run app
streamlit run src/ui/app.py
```

Open: **http://localhost:8501**

---

## Default Login

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin — goes to Admin Dashboard |
| any signup | your password | Analyst — goes to Home |

---

## Example Queries

**HDFS Dataset:**
```
Show all failed login attempts
Are there any brute force attacks?
Which IP addresses have the most failed connections?
Show me all blocked connections
What are the most common error types?
Are there any suspicious patterns?
Show all critical severity events
```

**BGL Dataset:**
```
Are there any hardware failures?
Show all fatal errors
What caused the most system crashes?
Are there any memory failures?
Show me all critical system alerts
Which nodes had the most errors?
Are there any kernel panic events?
```

**Upload your own file (CSV or TXT):**
```
Show all failed login attempts
Which users have the most authentication failures?
Are there any warning level events?
```

---

## Query Modes

| Mode | Response Time | Use When |
|------|--------------|----------|
| Fast | 1–3s | Quick check, exploring |
| Detailed | 3–6s | Investigating an issue |
| Deep Analysis | 5–10s | Full audit, thorough review |

---

## Key Files

```
src/ui/app.py                     Home page
src/ui/pages/0_Login.py           Login / Sign Up
src/ui/pages/1_Query_Logs.py      Main query interface
src/ui/pages/2_Analytics.py       Session analytics
src/ui/pages/3_Export.py          Export center
src/ui/pages/5_Admin.py           Admin dashboard
src/ui/pages/6_Benchmark.py       Metrics (admin only)
src/ui/auth/user_manager.py       User management
src/ui/auth/session.py            Session management
src/ui/utils/alert_system.py      Email alert system
src/rag_system/basic_rag_ollama.py    Groq + Gemini LLM
data/vector_db/HDFS_index.faiss   HDFS FAISS index
data/vector_db/BGL_index.faiss    BGL FAISS index
build_bgl_index.py                Run once to build BGL index
.env                              API keys (never commit)
```

---

## Environment Variables (.env)

```env
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
ALERT_EMAIL=your@gmail.com
ALERT_EMAIL_PASSWORD=abcdabcdabcdabcd
ALERT_RECIPIENT=recipient@gmail.com
```

---

## Roles and Access

| Page | Admin | Analyst | Viewer |
|------|-------|---------|--------|
| Home | ✅ | ✅ | ✅ |
| Query Logs | ✅ | ✅ | ✅ |
| Analytics | ✅ | ✅ | ✅ |
| Export | ✅ | ✅ | ✅ |
| Admin Dashboard | ✅ | ❌ | ❌ |
| Benchmark | ✅ | ❌ | ❌ |

---

## Benchmark Results (Reference)

| Metric | Score | Meaning |
|--------|-------|---------|
| Recall@5 | 1.000 | Perfect retrieval |
| MRR | 1.000 | Perfect ranking |
| Precision@5 | 0.400 | Good |
| ROUGE-1 | ~0.092 | Normal for RAG |
| Avg Time | ~7.4s | Acceptable |

---

## Quick Fixes

| Problem | Fix |
|---------|-----|
| App won't start | Activate venv, run `pip install -r requirements.txt` |
| API error | Check `.env` file has all 5 keys |
| Index not found | Run `python build_bgl_index.py` |
| Email not sending | Use Gmail App Password, not regular password |
| Forgot admin password | Delete `data/users.db`, restart app |
| Analytics empty | Run queries first, then refresh |
| Export shows sample | Run queries first in this session |
| Benchmark "access denied" | Must be logged in as admin |

---

## Alert Keywords (Triggers Email)

```
attack, brute force, unauthorized, authentication failure,
failed login, blocked, critical, malware, exploit, suspicious,
breach, compromised, privilege escalation, root access, fatal,
kernel panic, memory corruption, hardware failure, denial of service
```

---

**Full docs:** `docs/` folder | **Version:** 1.0.0 | **March 2026**
