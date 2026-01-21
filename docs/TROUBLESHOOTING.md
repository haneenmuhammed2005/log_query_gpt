# 🔧 Troubleshooting Guide

Comprehensive troubleshooting guide for ICS-LogQueryGPT.

---

## 📋 Table of Contents

- [Quick Diagnostics](#-quick-diagnostics)
- [Ollama Issues](#-ollama-issues)
- [Application Errors](#-application-errors)
- [Performance Problems](#-performance-problems)
- [Data & Index Issues](#-data--index-issues)
- [Network & Connection](#-network--connection)
- [Memory & Resource Issues](#-memory--resource-issues)

---

## 🔍 Quick Diagnostics

### Run System Test

```bash
# Comprehensive system test
python tests/test_complete_system.py
```

**Expected Output:**
```
✅ Passed:   7
⚠️  Warnings: 0
❌ Failed:   0
🎉 ALL TESTS PASSED!
```

### Check Service Status

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check if app is accessible
curl http://localhost:8501

# List Ollama models
ollama list
```

---

## 🤖 Ollama Issues

### Issue 1: "Connection refused" / "Ollama not responding"

**Symptoms:**
- `Connection refused` errors
- `Failed to connect to Ollama` messages
- Timeouts when generating responses

**Diagnosis:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Check Ollama port
netstat -tuln | grep 11434  # Linux/Mac
netstat -an | findstr 11434  # Windows

# Test connection
curl http://localhost:11434/api/tags
```

**Solutions:**

**Solution 1: Start Ollama**
```bash
# Linux/Mac
ollama serve

# Windows
# Ollama should start automatically, or run from Start Menu

# Verify it started
curl http://localhost:11434/api/tags
```

**Solution 2: Check Port Conflicts**
```bash
# Find what's using port 11434
lsof -i :11434  # Linux/Mac
netstat -ano | findstr :11434  # Windows

# Kill conflicting process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

**Solution 3: Reinstall Ollama**
```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download and reinstall from https://ollama.com/download
```

---

### Issue 2: "Model not found"

**Symptoms:**
- `model 'llama3.1:8b' not found`
- Empty model list
- Model pull fails

**Diagnosis:**
```bash
# List installed models
ollama list

# Try to run model directly
ollama run llama3.1:8b
```

**Solutions:**

**Solution 1: Pull the Model**
```bash
# Pull 8B model (recommended)
ollama pull llama3.1:8b

# Verify download
ollama list

# Test model
ollama run llama3.1:8b "Hello"
```

**Solution 2: Check Disk Space**
```bash
# Check available space (need ~5GB for 8B model)
df -h  # Linux/Mac
dir C:\  # Windows

# If low on space, clean up
ollama rm <unused-model>
```

**Solution 3: Check Network**
```bash
# Test connection to Ollama registry
ping registry.ollama.ai

# Try with proxy if needed
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
ollama pull llama3.1:8b
```

---

### Issue 3: Slow Model Responses

**Symptoms:**
- Generation takes >30 seconds
- Model feels sluggish
- High CPU usage

**Diagnosis:**
```bash
# Check system resources
top  # Linux/Mac
taskmgr  # Windows

# Check model size
ollama show llama3.1:8b

# Check if GPU is being used
nvidia-smi  # If you have NVIDIA GPU
```

**Solutions:**

**Solution 1: Use Smaller Model**
```python
# In src/ui/enhanced_app_ollama.py, change:
model_name = 'llama3.1:8b'  # Instead of 70b
```

**Solution 2: Reduce Context Length**
```python
# Reduce number of logs retrieved
num_logs = 3  # Instead of 10
```

**Solution 3: Enable GPU (if available)**
```bash
# Install CUDA drivers
# Download from: https://developer.nvidia.com/cuda-downloads

# Verify GPU detection
nvidia-smi

# Ollama will automatically use GPU if available
```

**Solution 4: Close Other Applications**
- Close browser tabs
- Stop other Python processes
- Restart Ollama service

---

## 🖥️ Application Errors

### Issue 4: Streamlit Won't Start

**Symptoms:**
- `streamlit: command not found`
- Port 8501 already in use
- Import errors

**Diagnosis:**
```bash
# Check if streamlit is installed
pip show streamlit

# Check if port is in use
netstat -tuln | grep 8501  # Linux/Mac
netstat -an | findstr 8501  # Windows

# Check Python path
which python  # Linux/Mac
where python  # Windows
```

**Solutions:**

**Solution 1: Activate Virtual Environment**
```bash
# Navigate to project directory
cd /path/to/ICS-LogQueryGPT

# Activate venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Verify
which python
pip list | grep streamlit
```

**Solution 2: Reinstall Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Solution 3: Use Different Port**
```bash
streamlit run src/ui/enhanced_app_ollama.py --server.port 8502
```

**Solution 4: Kill Existing Process**
```bash
# Linux/Mac
pkill -f streamlit

# Windows
taskkill /F /IM streamlit.exe
```

---

### Issue 5: Import Errors / Module Not Found

**Symptoms:**
- `ModuleNotFoundError: No module named 'xxx'`
- `ImportError: cannot import name 'xxx'`

**Diagnosis:**
```bash
# Check installed packages
pip list

# Check Python path
python -c "import sys; print(sys.path)"

# Try importing problematic module
python -c "import transformers"
```

**Solutions:**

**Solution 1: Install Missing Packages**
```bash
# Install from requirements
pip install -r requirements.txt

# Or install specific package
pip install transformers
pip install sentence-transformers
pip install faiss-cpu
```

**Solution 2: Check sys.path**
```python
# At top of test_complete_system.py
import sys
sys.path.append('src')
```

**Solution 3: Reinstall Corrupted Package**
```bash
pip uninstall <package-name>
pip install <package-name>
```

---

### Issue 6: BERT/Embeddings Errors

**Symptoms:**
- `OSError: Can't load tokenizer`
- BERT download fails
- Embedding generation errors

**Diagnosis:**
```bash
# Check HuggingFace cache
ls ~/.cache/huggingface  # Linux/Mac
dir %USERPROFILE%\.cache\huggingface  # Windows

# Test BERT loading
python -c "from transformers import BertModel, BertTokenizer; BertModel.from_pretrained('bert-base-uncased')"
```

**Solutions:**

**Solution 1: Clear Cache and Redownload**
```bash
# Clear HuggingFace cache
rm -rf ~/.cache/huggingface  # Linux/Mac
rmdir /s %USERPROFILE%\.cache\huggingface  # Windows

# Rerun embedder
python src/embeddings/enhanced_embedder.py
```

**Solution 2: Manual Download**
```python
from transformers import BertModel, BertTokenizer

# Force download
model = BertModel.from_pretrained('bert-base-uncased', force_download=True)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', force_download=True)
```

**Solution 3: Use Offline Mode (if internet is limited)**
```bash
# Download on machine with internet
python src/embeddings/download_bert.py

# Copy .cache/huggingface to offline machine
```

---

## ⚡ Performance Problems

### Issue 7: Slow Search Performance

**Symptoms:**
- Search takes >1 second
- UI freezes during search
- Slow response times

**Diagnosis:**
```bash
# Check index size
ls -lh data/embeddings/*.npy

# Check system resources
top  # Linux/Mac
taskmgr  # Windows
```

**Solutions:**

**Solution 1: Rebuild Optimized Index**
```bash
# Rebuild with IVF index for large datasets
python src/vector_db/optimized_search.py
```

**Solution 2: Reduce Dataset Size**
```python
# In process_all_data.py, limit rows
df = df.head(1000)  # Use only 1000 logs for testing
```

**Solution 3: Use GPU for Search**
```bash
# Install GPU-enabled FAISS
pip uninstall faiss-cpu
pip install faiss-gpu
```

---

### Issue 8: High Memory Usage

**Symptoms:**
- System runs out of RAM
- Process killed
- Swap usage high

**Diagnosis:**
```bash
# Check memory usage
free -h  # Linux
vm_stat  # Mac
taskmgr  # Windows

# Check process memory
ps aux | grep python  # Linux/Mac
```

**Solutions:**

**Solution 1: Reduce Batch Size**
```python
# In enhanced_embedder.py
BATCH_SIZE = 8  # Reduce from 32
```

**Solution 2: Use Smaller Model**
```bash
# Switch to 8B instead of 70B
ollama pull llama3.1:8b
```

**Solution 3: Clear Python Cache**
```python
import gc
gc.collect()
```

**Solution 4: Increase Swap (Linux)**
```bash
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📁 Data & Index Issues

### Issue 9: "File not found" Errors

**Symptoms:**
- `FileNotFoundError: data/embeddings/HDFS_enhanced.npy`
- Missing CSV files
- Empty results

**Diagnosis:**
```bash
# Check data directory structure
tree data/  # Linux/Mac
dir /s data\  # Windows

# List specific files
ls data/embeddings/
ls data/processed_logs/
```

**Solutions:**

**Solution 1: Run Data Pipeline**
```bash
# Complete data preparation
python src/preprocessing/download_data.py
python src/preprocessing/process_all_data.py
python src/embeddings/enhanced_embedder.py
python src/vector_db/optimized_search.py
```

**Solution 2: Check File Permissions**
```bash
# Fix permissions (Linux/Mac)
chmod -R 755 data/
chmod 644 data/embeddings/*.npy
chmod 644 data/processed_logs/*.csv
```

**Solution 3: Verify File Integrity**
```python
import numpy as np
import pandas as pd

# Test loading
emb = np.load('data/embeddings/HDFS_enhanced.npy')
df = pd.read_csv('data/processed_logs/HDFS_enhanced.csv')

print(f"Embeddings: {emb.shape}")
print(f"Dataframe: {len(df)} rows")
```

---

### Issue 10: Index Build Fails

**Symptoms:**
- Index building crashes
- FAISS errors
- Dimension mismatch errors

**Diagnosis:**
```bash
# Run test
python tests/test_complete_system.py

# Check embedding dimensions
python -c "import numpy as np; e = np.load('data/embeddings/HDFS_enhanced.npy'); print(e.shape)"
```

**Solutions:**

**Solution 1: Rebuild Everything**
```bash
# Clean and rebuild
rm -rf data/embeddings/*
rm -rf data/processed_logs/*

# Regenerate
python src/preprocessing/process_all_data.py
python src/embeddings/enhanced_embedder.py
python src/vector_db/optimized_search.py
```

**Solution 2: Check Dimension Match**
```python
# Embeddings should be (N, 768)
# Dataframe should have N rows
import numpy as np
import pandas as pd

emb = np.load('data/embeddings/HDFS_enhanced.npy')
df = pd.read_csv('data/processed_logs/HDFS_enhanced.csv')

assert emb.shape[0] == len(df), "Mismatch!"
assert emb.shape[1] == 768, "Wrong dimensions!"
```

---

## 🌐 Network & Connection

### Issue 11: Docker Networking Issues

**Symptoms:**
- Can't access app from host
- Container can't reach Ollama
- Port conflicts

**Solutions:**

**Solution 1: Check Port Mapping**
```bash
# View container ports
docker ps

# Check if ports are mapped correctly
docker inspect <container-id> | grep PortBindings
```

**Solution 2: Use Host Network**
```yaml
# In docker-compose.yml
network_mode: "host"
```

**Solution 3: Check Firewall**
```bash
# Linux
sudo ufw allow 8501/tcp
sudo ufw allow 11434/tcp

# Docker
sudo systemctl restart docker
```

---

## 🧠 Memory & Resource Issues

### Issue 12: "Killed" / Process Terminated

**Symptoms:**
- Process suddenly stops
- "Killed" message
- OOM (Out of Memory) errors

**Solutions:**

**Solution 1: Monitor Memory**
```bash
# Watch memory in real-time
watch -n 1 free -h

# Check dmesg for OOM killer
dmesg | grep -i kill
```

**Solution 2: Reduce Memory Usage**
```python
# Reduce batch sizes
EMBEDDING_BATCH_SIZE = 8
RETRIEVAL_LOGS = 3

# Use 8B model
MODEL = "llama3.1:8b"
```

**Solution 3: Add Swap Space**
```bash
# Create 8GB swap
sudo dd if=/dev/zero of=/swapfile bs=1G count=8
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🆘 Emergency Recovery

### Complete Reset

```bash
# Stop all services
pkill -f ollama
pkill -f streamlit

# Clean virtual environment
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Clean data
rm -rf data/embeddings/*
rm -rf data/processed_logs/*

# Reinstall Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b

# Rebuild everything
python src/preprocessing/download_data.py
python src/preprocessing/process_all_data.py
python src/embeddings/enhanced_embedder.py
python src/vector_db/optimized_search.py

# Run tests
python tests/test_complete_system.py

# Start application
ollama serve &
streamlit run src/ui/enhanced_app_ollama.py
```

---

## 📞 Getting Help

If you're still experiencing issues:

1. **Check Logs:**
   ```bash
   # Application logs
   tail -f logs/app.log
   
   # System logs
   journalctl -u ics-logquery -f
   ```

2. **Run Diagnostics:**
   ```bash
   python tests/test_complete_system.py
   ```

3. **Create GitHub Issue:**
   - Include error messages
   - Include system info
   - Include steps to reproduce
   - [Open Issue](https://github.com/yourusername/ICS-LogQueryGPT/issues)

4. **Contact Support:**
   - Email: team@example.com
   - Include diagnostic output

---

## 📚 Additional Resources

- [User Guide](USER_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Technical Documentation](TECHNICAL.md)
- [Ollama Documentation](https://ollama.ai/docs)
- [Streamlit Documentation](https://docs.streamlit.io)

---

**Version**: 1.0.0  
**Last Updated**: January 21, 2026