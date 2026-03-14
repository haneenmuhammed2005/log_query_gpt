# Deployment Guide

Complete guide for running ICS-LogQueryGPT locally or with Docker.

---

## Table of Contents

- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [Building FAISS Indexes](#building-faiss-indexes)
- [Running the App](#running-the-app)
- [Docker Deployment](#docker-deployment)
- [Production Notes](#production-notes)

---

## Local Setup

### Prerequisites

- Python 3.8 or higher
- pip
- Git
- Internet connection (for Groq and Gemini APIs)

### Step 1: Clone the Repository

```bash
git clone https://github.com/haneenmuhammed2005/ICS-LogQueryGPT.git
cd ICS-LogQueryGPT
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Streamlit, LangChain, Groq, Gemini, sentence-transformers, FAISS, transformers, and all other dependencies.

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ALERT_EMAIL=your_gmail@gmail.com
ALERT_EMAIL_PASSWORD=your_16char_app_password
ALERT_RECIPIENT=recipient@gmail.com
```

**Getting API Keys:**

| Key | Where to Get |
|-----|-------------|
| GROQ_API_KEY | [console.groq.com](https://console.groq.com) → free tier available |
| GOOGLE_API_KEY | [aistudio.google.com](https://aistudio.google.com) → free tier available |
| ALERT_EMAIL_PASSWORD | Google Account → Security → App Passwords (16-char) |

### Step 5: Build FAISS Indexes

Run this once to build the BGL vector index:

```bash
python build_bgl_index.py
```

The HDFS index should already be present. If not, check that `data/vector_db/` contains:
- `HDFS_index.faiss`
- `HDFS_metadata.pkl`
- `BGL_index.faiss`
- `BGL_metadata.pkl`

### Step 6: Launch the App

```bash
streamlit run src/ui/app.py
```

Open your browser at **http://localhost:8501**

---

## Environment Variables

Full reference for `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for llama-3.1-8b-instant |
| `GOOGLE_API_KEY` | Yes | Google API key for Gemini Flash fallback |
| `ALERT_EMAIL` | Yes | Gmail address that sends alert emails |
| `ALERT_EMAIL_PASSWORD` | Yes | Gmail App Password (16 chars, not your regular password) |
| `ALERT_RECIPIENT` | Yes | Email address that receives alerts |

The `.env` file is loaded automatically at startup via `python-dotenv`. Never commit this file to git — it is already in `.gitignore`.

---

## Building FAISS Indexes

If you need to rebuild the indexes from scratch:

```bash
# Rebuild BGL index
python build_bgl_index.py

# The HDFS index is built from the HDFS dataset CSV
# Place HDFS.log_structured.csv in data/ and run the embedder
```

Indexes are stored in `data/vector_db/` and loaded at query time. Building takes 5–10 minutes on CPU due to BERT embedding generation.

---

## Running the App

### Standard Launch

```bash
streamlit run src/ui/app.py
```

### Custom Port

```bash
streamlit run src/ui/app.py --server.port 8502
```

### Hide Streamlit Menu (Production)

Add to `.streamlit/config.toml`:

```toml
[server]
headless = true

[browser]
gatherUsageStats = false

[ui]
hideSidebarNav = true
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p data/vector_db data/sessions .cache

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start app
CMD ["streamlit", "run", "src/ui/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  ics-logquery:
    build: .
    container_name: ics-logquerygpt
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./.cache:/app/.cache
      - ./.env:/app/.env
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

### Build and Run

```bash
# Build image
docker build -t ics-logquerygpt .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker Notes

- Mount `./data` as a volume so FAISS indexes and databases persist between restarts
- Mount `./.env` so API keys are passed in without baking them into the image
- Build takes 5–10 minutes the first time due to PyTorch and transformers installation
- Container needs internet access for Groq and Gemini API calls

---

## Production Notes

### Security

- Change the default admin password immediately after first login
- Use HTTPS with a reverse proxy (Nginx/Caddy) in production
- Keep your `.env` file out of version control
- Rotate your Gmail App Password periodically

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    location /_stcore/stream {
        proxy_pass http://localhost:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

### Performance Tips

- Pre-build FAISS indexes before deploying — do not build at startup
- Use SSD storage for `data/vector_db/` for faster index loading
- Set `GROQ_API_KEY` to a paid tier key for higher rate limits if running many concurrent users

---

## Checklist

Before going live:

- [ ] `.env` file created with all 5 variables set
- [ ] FAISS indexes present in `data/vector_db/`
- [ ] App runs at `http://localhost:8501`
- [ ] Can log in as admin
- [ ] Can run a query and get a response
- [ ] Alert email works (test by querying "are there brute force attacks")
- [ ] Default admin password changed

---

**Version:** 1.0.0 | **Last Updated:** March 2026
