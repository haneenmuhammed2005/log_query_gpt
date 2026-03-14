# Troubleshooting Guide

Common issues and fixes for ICS-LogQueryGPT.

---

## Table of Contents

- [App Won't Start](#app-wont-start)
- [API Key Errors](#api-key-errors)
- [FAISS / Index Errors](#faiss--index-errors)
- [BERT / Embedding Errors](#bert--embedding-errors)
- [Email Alert Not Sending](#email-alert-not-sending)
- [Login Issues](#login-issues)
- [Slow Responses](#slow-responses)
- [Analytics Shows No Data](#analytics-shows-no-data)
- [Export Shows Sample Data](#export-shows-sample-data)
- [Benchmark Errors](#benchmark-errors)

---

## App Won't Start

**Error:** `streamlit: command not found`

```bash
# Make sure virtual environment is activated
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt

# Try running directly
python -m streamlit run src/ui/app.py
```

**Error:** `Port 8501 already in use`

```bash
# Use a different port
streamlit run src/ui/app.py --server.port 8502

# Or kill the existing process
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8501 | xargs kill -9
```

**Error:** `ModuleNotFoundError: No module named 'langchain_groq'`

```bash
pip install langchain-groq langchain-google-genai langchain-core
```

**Error:** `ModuleNotFoundError: No module named 'faiss'`

```bash
pip install faiss-cpu
```

---

## API Key Errors

**Error:** `AuthenticationError: Invalid API key` (Groq)

1. Check your `.env` file has `GROQ_API_KEY=gsk_...`
2. Verify the key at [console.groq.com](https://console.groq.com)
3. Make sure `load_dotenv()` is called before the API is used
4. Restart the Streamlit app after editing `.env`

**Error:** Groq rate limit exceeded

The system automatically falls back to Gemini Flash. If both fail, wait 1 minute and retry. Free Groq tier allows 30 requests/minute.

**Error:** `google.api_core.exceptions.InvalidArgument` (Gemini)

1. Check your `.env` has `GOOGLE_API_KEY=AIza...`
2. Verify at [aistudio.google.com](https://aistudio.google.com)
3. Make sure the Gemini API is enabled for your project

---

## FAISS / Index Errors

**Error:** `FileNotFoundError: data/vector_db/BGL_index.faiss`

```bash
# Rebuild BGL index
python build_bgl_index.py
```

**Error:** `FileNotFoundError: data/vector_db/HDFS_index.faiss`

The HDFS index should come with the repository. If missing, check that `data/vector_db/` directory exists and contains the 4 required files:
- `HDFS_index.faiss`
- `HDFS_metadata.pkl`
- `BGL_index.faiss`
- `BGL_metadata.pkl`

**Error:** `ValueError: Dimension mismatch`

The FAISS index and BERT model dimensions must both be 768. If you see this error, the index may be corrupted. Delete and rebuild:

```bash
del data\vector_db\BGL_index.faiss
del data\vector_db\BGL_metadata.pkl
python build_bgl_index.py
```

---

## BERT / Embedding Errors

**Error:** `OSError: Can't load tokenizer for 'bert-base-uncased'`

The model needs to download on first use. Make sure you have internet access. The cache is stored at:
```
D:/Projects/log_query_gpt/.cache/huggingface
```

If the cache is corrupted:
```bash
# Delete cache and let it re-download
rmdir /s "D:\Projects\log_query_gpt\.cache\huggingface"
```

**Error:** Embedding takes too long (>60 seconds per query)

This is normal on first run — BERT model loads into memory. Subsequent queries are much faster (200ms). If every query is slow, check that your `HF_HOME` cache path is set correctly in the page files.

---

## Email Alert Not Sending

**Error:** `SMTPAuthenticationError: Email authentication failed`

The most common cause is using your regular Gmail password instead of an App Password.

To generate an App Password:
1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click Security
3. Enable 2-Step Verification (required)
4. Go to App Passwords
5. Create a new app password for "Mail"
6. Copy the 16-character code (no spaces) into your `.env`

```env
ALERT_EMAIL_PASSWORD=abcdabcdabcdabcd
```

**Error:** Alert banner shows but email not sent

Check the error message shown in the banner. Common causes:
- Wrong App Password
- Gmail account has "Less secure app access" restrictions (use App Password instead)
- Network firewall blocking port 465

**Alert not triggering at all**

The query response must contain one of the critical keywords. Try:
- "Show all brute force attacks"
- "Are there any unauthorized access attempts"
- "What critical errors are in the logs"

---

## Login Issues

**Can't log in with admin / admin123**

The default admin account is created only if the users database is empty. If you already have users, the admin account may already exist. Try logging in, and if it fails, check `data/users.db` with a SQLite viewer.

**Forgot password**

There is no password reset UI. An admin can delete and recreate your account from the Admin Dashboard. If you forgot the admin password, delete `data/users.db` and restart the app — a fresh admin account will be created.

**Session expired after 30 minutes**

Sessions expire after 30 minutes of inactivity. Log in again. The session timeout cannot be changed from the UI but can be adjusted in `src/ui/auth/session.py` by changing `timeout_minutes`.

---

## Slow Responses

**Queries take 15–30 seconds**

Normal causes:
- First query of the session (BERT model loading into memory)
- Groq API is experiencing high load — system falls back to Gemini which may be slower
- Using Deep Analysis mode with 8 retrieved logs

To improve speed:
- Use **Fast** mode for routine queries
- Wait for the first query to complete before running more (model stays loaded)
- Check your internet speed — Groq API needs a stable connection

---

## Analytics Shows No Data

The Analytics page only shows data from the current session. You must run queries first.

1. Go to Query Logs
2. Run at least 3–5 different queries
3. Come back to Analytics
4. Click **Refresh Data** in the sidebar

---

## Export Shows Sample Data

The Export page shows sample data when no queries have been run in the current session. This is expected behavior.

The header says "Sample Data — run queries to export real results" when showing sample data. After running queries, it will say "Query History — X queries from this session".

---

## Benchmark Errors

**Benchmark page shows "Access denied"**

The Benchmark page is admin-only. Log in as `admin` to access it.

**Benchmark runs but all scores are 0.0**

This means the RAG system threw an error for each test question. Check:
1. GROQ_API_KEY is set and valid
2. FAISS indexes exist for both HDFS and BGL
3. The `ICSLogQueryGPTOllama` class loads without error

**Overall Quality shows "Poor"**

This is a display label based on ROUGE-1 score thresholds calibrated for RAG systems:
- ≥ 0.30 = Excellent
- ≥ 0.15 = Good
- ≥ 0.05 = Fair
- < 0.05 = Poor

BLEU and ROUGE scores being low is expected for RAG systems — see the TECHNICAL.md for context. The important metrics are **Recall@5 = 1.0** and **MRR = 1.0**.

---

## Getting More Help

1. Check the error message carefully — most errors contain the exact problem
2. Restart the Streamlit app (Ctrl+C, then `streamlit run src/ui/app.py`)
3. Check that `.env` has all 5 variables set correctly
4. Check that `data/vector_db/` has all 4 index files
5. Open an issue on GitHub with the full error message and steps to reproduce

---

**Version:** 1.0.0 | **Last Updated:** March 2026
