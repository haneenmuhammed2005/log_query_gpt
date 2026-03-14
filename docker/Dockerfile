FROM python:3.13-slim

WORKDIR /app

# Install curl
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY .streamlit/ ./.streamlit/

# Create directories
RUN mkdir -p data/logs data/faiss_index data/cache

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start Streamlit
CMD streamlit run src/ui/pages/0_🔐_Login.py \
    --server.address=0.0.0.0 \
    --server.port=8501 \
    --server.headless=true