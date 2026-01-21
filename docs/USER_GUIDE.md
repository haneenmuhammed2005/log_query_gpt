# 📘 ICS-LogQueryGPT - User Guide

## 🎯 Overview

ICS-LogQueryGPT is a production-ready system for analyzing Industrial Control System (ICS) logs using advanced AI. It combines:

- **Local LLM**: Llama 3.1 via Ollama (100% private)
- **Vector Search**: FAISS for fast similarity search
- **Smart Embeddings**: BERT for semantic understanding
- **Protocol Awareness**: Detects ICS protocols (Modbus, DNP3, SNMP, SSH, HTTP, FTP, Telnet, BACnet)
- **Conversational AI**: Memory-enabled chat interface

---

## 🚀 Quick Start

### 1. Prerequisites

**System Requirements:**
- **CPU**: 4+ cores recommended
- **RAM**: 16GB minimum, 32GB recommended for 70B model
- **Storage**: 10GB free space
- **GPU**: Optional (speeds up inference significantly)
- **OS**: Windows 10/11, Linux, or macOS

**Software:**
- Python 3.8+
- Ollama
- Git

### 2. Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ICS-LogQueryGPT.git
cd ICS-LogQueryGPT

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Ollama

**Windows:**
1. Download from https://ollama.com/download
2. Run the installer
3. Ollama will start automatically

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Pull Llama 3.1 Model:**
```bash
# Recommended: 8B model (faster, runs on most hardware)
ollama pull llama3.1:8b

# Optional: 70B model (more accurate, requires GPU)
ollama pull llama3.1:70b
```

**Verify Installation:**
```bash
ollama list
# Should show llama3.1:8b in the list
```

### 4. Prepare Data

```bash
# Download and process logs
python src/preprocessing/download_data.py
python src/preprocessing/process_all_data.py

# Create embeddings (this may take 5-10 minutes)
python src/embeddings/enhanced_embedder.py

# Build optimized vector index
python src/vector_db/optimized_search.py
```

### 5. Launch Application

**Terminal 1 - Start Ollama (if not already running):**
```bash
ollama serve
```

**Terminal 2 - Launch Web Interface:**
```bash
streamlit run src/ui/enhanced_app_ollama.py
```

**Access the application at:** http://localhost:8501

---

## 💡 Usage Guide

### Basic Query Examples

#### **Authentication Issues:**
```
Show me authentication failures
Find SSH login errors
Who tried to log in from suspicious IPs?
List all failed authentication attempts
```

#### **Protocol-Specific Queries:**
```
Find Modbus communication errors
Show DNP3 timeout issues
What SNMP traps occurred?
List all HTTP request failures
Show BACnet device offline events
```

#### **Security Analysis:**
```
Are there any security concerns?
Identify suspicious patterns in the logs
Show critical security events
What unauthorized access attempts occurred?
Analyze potential security breaches
```

#### **Troubleshooting:**
```
Why did device 5 fail?
Explain this Modbus error
What caused the timeout on the outstation?
Debug the communication failure
Root cause analysis for system errors
```

### Advanced Features

#### **1. Protocol Filtering**
- Select specific protocols from the sidebar
- Focuses search on relevant logs only
- Available protocols: Modbus, DNP3, SNMP, SSH, HTTP, FTP, Telnet, BACnet
- Improves answer relevance and speed

#### **2. Severity Filtering**
- Filter by: Critical, High, Medium, Low, Info
- Quickly identify urgent issues
- Prioritize investigation based on severity
- Combine with protocol filters for precise queries

#### **3. Analysis Modes**

**Analysis Mode:**
- Detailed step-by-step examination
- Breaks down complex issues
- Best for: Understanding what happened

**Summary Mode:**
- Quick overview of events
- Condensed information
- Best for: Getting the big picture

**Security Mode:**
- Security-focused analysis
- Identifies threats and vulnerabilities
- Best for: Security audits and incident response

**Troubleshooting Mode:**
- Problem diagnosis and solutions
- Root cause analysis
- Best for: Fixing issues and preventing recurrence

#### **4. Conversation Memory**

The system remembers your conversation context:

```
You: "Show me authentication failures"
System: [Lists 5 authentication failures]

You: "Which IP address was most frequent?"
System: [Analyzes the previous results and identifies the IP]

You: "Is this a security concern?"
System: [Provides security analysis based on the full context]
```

**Export Conversations:**
- Click "Export Conversation" to save history
- JSON format for easy review
- Includes all questions, answers, and metadata

---

## ⚙️ Configuration

### Retrieval Settings

**Number of Logs to Retrieve (1-20)**
- **More logs** = Better context, slower responses
- **Fewer logs** = Faster responses, may miss context
- **Recommended**: 5-7 logs
- **Default**: 5 logs

**Minimum Similarity Score (0.0-1.0)**
- **Higher** (0.7-1.0) = Stricter matching, more relevant
- **Lower** (0.3-0.5) = Broader results, may include less relevant logs
- **Recommended**: 0.3-0.5 for exploratory queries
- **Default**: 0.3

### Generation Settings

**Temperature (0.0-1.0)**
- **0.0-0.3**: Focused, deterministic, factual
- **0.4-0.7**: Balanced (recommended for most use cases)
- **0.8-1.0**: Creative, diverse, less predictable
- **Default**: 0.7

**Model Selection**
- **llama3.1:8b**: Fast, works on most hardware (4GB+ RAM)
- **llama3.1:70b**: More accurate, requires powerful GPU (40GB+ VRAM)
- **Recommendation**: Start with 8B, upgrade to 70B if accuracy is critical

---

## 🔧 Troubleshooting

### Common Issues

#### **1. "Connection refused" / "Ollama not found"**

**Symptoms:**
- Error connecting to Ollama
- Timeouts when generating responses
- "Connection refused" errors

**Solutions:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# Verify model is available
ollama list
```

#### **2. "Model not found"**

**Symptoms:**
- "Model llama3.1:8b not found" error
- Empty model list

**Solutions:**
```bash
# Pull the model
ollama pull llama3.1:8b

# Verify it's installed
ollama list

# Check model size
ollama show llama3.1:8b
```

#### **3. Slow Response Times**

**Symptoms:**
- Generation takes >30 seconds
- UI feels sluggish
- System becomes unresponsive

**Solutions:**
1. **Use smaller model**: Switch from 70B to 8B
2. **Reduce retrieved logs**: Set to 3-5 instead of 10+
3. **Lower temperature**: Set to 0.3-0.5
4. **Close other apps**: Free up RAM and CPU
5. **Check GPU**: Ensure CUDA is properly configured (if using GPU)

**Performance Benchmarks:**
- **8B model**: 3-8 seconds per response (CPU)
- **8B model**: 1-3 seconds per response (GPU)
- **70B model**: 15-30 seconds per response (GPU required)

#### **4. "Index not found" / "File not found"**

**Symptoms:**
- Can't load embeddings
- "FileNotFoundError" for .npy or .csv files
- Empty search results

**Solutions:**
```bash
# Re-run the embedding pipeline
python src/embeddings/enhanced_embedder.py

# Rebuild the vector index
python src/vector_db/optimized_search.py

# Verify files exist
dir data\embeddings\HDFS_enhanced.npy    # Windows
dir data\processed_logs\HDFS_enhanced.csv

ls data/embeddings/HDFS_enhanced.npy     # Linux/Mac
ls data/processed_logs/HDFS_enhanced.csv
```

#### **5. Out of Memory Errors**

**Symptoms:**
- System crashes
- "Out of memory" errors
- Python process killed

**Solutions:**
1. **Use 8B model** instead of 70B
2. **Reduce batch size** in `config.py`: Set `BATCH_SIZE = 16` or `8`
3. **Close other applications** to free RAM
4. **Restart Ollama**: `ollama serve`
5. **Upgrade hardware**: Add more RAM if possible

#### **6. Streamlit Won't Start**

**Symptoms:**
- Port 8501 already in use
- Streamlit doesn't launch

**Solutions:**
```bash
# Kill existing Streamlit processes
# Windows:
taskkill /F /IM streamlit.exe

# Linux/Mac:
pkill -f streamlit

# Use different port
streamlit run src/ui/enhanced_app_ollama.py --server.port 8502
```

---

## 📊 Understanding Results

### Result Components

#### **1. Generated Answer**
- AI-generated response from Llama 3.1
- Cites specific log entries (Log 1, Log 2, etc.)
- Provides context and explanations
- Offers actionable insights

#### **2. Retrieved Logs**
- Source logs used to generate the answer
- Ranked by similarity score (highest first)
- Shows:
  - Original log text
  - Detected protocols
  - Severity level
  - Similarity score

#### **3. Metadata**
- **Generation time**: How long the AI took to respond
- **Analysis mode**: Which mode was used
- **Model version**: Which Llama model generated the response
- **Conversation position**: Turn number in the conversation

### Interpreting Similarity Scores

| Score Range | Relevance | Description |
|-------------|-----------|-------------|
| **0.9-1.0** | Highly relevant | Nearly identical to query intent |
| **0.7-0.9** | Very relevant | Strong semantic match |
| **0.5-0.7** | Moderately relevant | Related but not exact |
| **0.3-0.5** | Potentially relevant | Weak connection, may still be useful |
| **<0.3** | Low relevance | Likely not useful (filtered out by default) |

---

## 🆚 Comparison: Ollama vs OpenAI

| Feature | **Ollama (This System)** | **OpenAI API** |
|---------|--------------------------|----------------|
| **Cost** | Free (one-time setup) | ~$0.002-0.01 per query |
| **Privacy** | 100% local, no data sent out | Data sent to OpenAI servers |
| **Internet** | Not required after setup | Required for every query |
| **Speed** | Depends on hardware (3-8s typical) | Very fast (1-3s) |
| **Accuracy** | Very good (Llama 3.1) | Excellent (GPT-4) |
| **Setup Complexity** | More complex initial setup | Simple (just API key) |
| **Customization** | Full control over everything | Limited customization |
| **Data Security** | Complete control | Must trust third party |
| **Offline Use** | Yes (after initial setup) | No |
| **Model Updates** | Manual (`ollama pull`) | Automatic |

**Recommendation**: Use Ollama for:
- ✅ Sensitive/proprietary data
- ✅ Offline/air-gapped environments
- ✅ Cost-conscious deployments
- ✅ Full control requirements
- ✅ Long-term sustainable solution

---

## 🔒 Security & Privacy

### Data Privacy Guarantees

- **100% Local Processing**: All data stays on your machine
- **No External API Calls**: Except initial model download
- **No Telemetry**: No usage data sent to any server
- **Your Data Stays Yours**: Complete ownership and control
- **No Internet Required**: After initial setup

### Security Best Practices

1. **Keep Ollama Updated**: 
   ```bash
   ollama update
   ```

2. **Regular Backups**: 
   - Export important conversations
   - Backup your processed logs and embeddings

3. **Access Control**: 
   - Run on localhost only (default)
   - Use firewall rules if needed
   - Consider authentication for production

4. **Monitor Resources**: 
   - Watch CPU/RAM usage
   - Set up alerts for anomalies

5. **Review Logs**: 
   - Check system logs periodically
   - Monitor for unusual queries

---

## 📝 Tips & Best Practices

### Query Writing Tips

**❌ Bad Query:**
```
Show errors
```

**✅ Good Query:**
```
Show Modbus write errors on device 5 in the last hour
```

---

**❌ Vague:**
```
What happened?
```

**✅ Specific:**
```
What authentication failures occurred from IP 192.168.1.100?
```

---

**❌ Single Question:**
```
Analyze all security issues
```

**✅ Follow-Up Conversation:**
```
1. "Show me critical security events"
2. "Which devices were affected?"
3. "What's the root cause?"
4. "How can we prevent this?"
```

### Performance Optimization Tips

1. **Start Simple**: Begin with basic queries, then add complexity
2. **Use Filters**: Apply protocol and severity filters to narrow results
3. **Right Model for the Job**: 
   - Use 8B for quick explorations
   - Use 70B for critical analysis
4. **Manage Conversation History**: 
   - Clear old conversations to free memory
   - Export and archive important sessions
5. **Batch Similar Queries**: Ask related questions in one conversation

### Getting the Best Answers

1. **Provide Context**: Mention specific devices, time ranges, or protocols
2. **Ask Follow-ups**: Build on previous answers for deeper insights
3. **Specify Output Format**: "List the top 5...", "Summarize in 3 points..."
4. **Use the Right Mode**: Security mode for threats, Troubleshooting for fixes
5. **Adjust Retrieval**: If answers lack context, increase retrieved logs

---

## 🎓 Learning Resources

### ICS/SCADA Protocols
- [Modbus Protocol Guide](https://modbus.org)
- [DNP3 User Group](https://www.dnp.org)
- [SNMP RFC Documentation](https://www.ietf.org/rfc/rfc1157.txt)
- [BACnet International](https://www.bacnet.org)

### AI & RAG Systems
- [Llama 3.1 Announcement](https://ai.meta.com/blog/meta-llama-3-1/)
- [RAG Explained (Pinecone)](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [FAISS Documentation](https://faiss.ai)
- [BERT Paper](https://arxiv.org/abs/1810.04805)

### Vector Databases & Embeddings
- [Understanding Vector Search](https://www.pinecone.io/learn/vector-search/)
- [Sentence Transformers](https://www.sbert.net)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)

---

## 📞 Support & Resources

### Documentation
- **User Guide**: `docs/USER_GUIDE.md` (this file)
- **Technical Documentation**: `docs/TECHNICAL.md`
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **API Reference**: `docs/API.md`

### Getting Help

**GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/ICS-LogQueryGPT/issues)

**Before opening an issue:**
1. Check existing issues
2. Run the test suite: `python tests/test_complete_system.py`
3. Include system info and error messages

### Project Information
- **Version**: 1.0.0
- **Last Updated**: January 21, 2026
- **License**: MIT
- **Maintained by**: ICS-LogQueryGPT Team

---

## 🚀 Next Steps

### After Mastering the Basics

1. **Explore Advanced Queries**: Try complex multi-part questions
2. **Customize Settings**: Fine-tune retrieval and generation parameters
3. **Add Your Own Logs**: Extend beyond HDFS dataset
4. **Integrate with Tools**: Connect to monitoring systems
5. **Contribute**: Submit improvements to the project

### Optional Features to Enable

- **Email Alerts**: Get notified of critical events
- **Slack Integration**: Query logs from Slack
- **REST API**: Build custom integrations
- **Multi-Language**: Add support for other languages
- **Advanced Analytics**: Build custom dashboards

---

**Need help? Have questions?** 

Open an issue on GitHub or check our comprehensive troubleshooting guide!

---

*Built with ❤️ for the ICS/SCADA community*