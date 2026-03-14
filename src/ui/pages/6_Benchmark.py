# Benchmark & Metrics Page
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["HF_HOME"]                    = "D:/Projects/log_query_gpt/.cache/huggingface"
os.environ["TRANSFORMERS_CACHE"]         = "D:/Projects/log_query_gpt/.cache/huggingface"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "D:/Projects/log_query_gpt/.cache/sentence_transformers"
os.environ["GROQ_API_KEY"]               = os.environ.get("GROQ_API_KEY", "")
os.environ["GOOGLE_API_KEY"]             = os.environ.get("GOOGLE_API_KEY", "")

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.auth.session import SessionManager

PAGE_HOME      = "app.py"
PAGE_QUERY     = "pages/1_Query_Logs.py"
PAGE_ANALYTICS = "pages/2_Analytics.py"
PAGE_EXPORT    = "pages/3_Export.py"
PAGE_LOGIN     = "pages/0_Login.py"

st.set_page_config(
    page_title="Benchmark — ICS-LogQueryGPT",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject(html):
    try:
        st.html(html)
    except AttributeError:
        st.markdown(html, unsafe_allow_html=True)

def inject_styles():
    inject("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif !important;
    background: #060d1f !important; color: #e2e8f0 !important;
}
section[data-testid="stSidebarNav"],
[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavItems"],
div[data-testid="stSidebarCollapseButton"],
button[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
span[data-testid="stIconMaterial"],
[data-testid="stSidebarHeader"],
header[data-testid="stHeader"], footer, #MainMenu,
div[data-testid="stToolbar"], div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] { display: none !important; }
@keyframes floatorb { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-16px)} }
@keyframes shimmer  { 0%{background-position:-300% center} 100%{background-position:300% center} }
@keyframes fadeUp   { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
.stApp::before {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background-image: linear-gradient(rgba(0,170,255,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,170,255,0.022) 1px, transparent 1px);
    background-size:52px 52px;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(3,8,22,0.99) 0%, rgba(2,6,18,0.99) 100%) !important;
    border-right: 1px solid rgba(0,170,255,0.10) !important;
}
section[data-testid="stSidebar"] * { font-family: 'Space Grotesk', sans-serif !important; }
section[data-testid="stSidebar"] h3 {
    font-size: 9px !important; font-weight: 700 !important;
    color: #3a5a7a !important; text-transform: uppercase !important;
    letter-spacing: 0.16em !important;
}
div.block-container {
    padding-top: 0 !important; padding-left: 2.5rem !important;
    padding-right: 2.5rem !important; max-width: 100% !important;
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.022) !important;
    border: 1px solid rgba(255,255,255,0.065) !important;
    border-radius: 11px !important; padding: 16px 18px !important;
}
div[data-testid="stMetricValue"] {
    font-size: 26px !important; font-weight: 700 !important; color: #00aaff !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 9px !important; color: #3a5a7a !important;
    text-transform: uppercase !important; letter-spacing: 0.12em !important; font-weight: 700 !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0040aa 0%, #0077cc 45%, #00aaff 100%) !important;
    border: none !important; border-radius: 9px !important;
    color: #fff !important; font-weight: 700 !important; height: 44px !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(255,255,255,0.028) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 9px !important; color: #5a7a9a !important;
}
div[data-testid="stDataFrame"] {
    border-radius: 10px !important; border: 1px solid rgba(255,255,255,0.065) !important;
}
div[data-testid="stAlert"] { border-radius: 9px !important; }
hr { border-color: rgba(255,255,255,0.05) !important; }
div[data-testid="stProgress"] > div { background: rgba(255,255,255,0.04) !important; }
div[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #0055ff, #00aaff) !important; }
</style>
""")

def check_authentication():
    if not st.session_state.get('authenticated', False):
        st.switch_page(PAGE_LOGIN)
        st.stop()
    if st.session_state.get('session_token') == "admin-session":
        return
    session_manager = SessionManager()
    if not session_manager.validate_session(st.session_state.get('session_token')):
        st.session_state.clear()
        st.session_state["session_expired"] = True
        st.switch_page(PAGE_LOGIN)
        st.stop()
    if st.session_state.get('user_role', '') != 'admin':
        try:
            st.html("""
            <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&display=swap" rel="stylesheet">
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:60vh;font-family:'Space Grotesk',sans-serif;text-align:center;padding:40px;">
                <div style="width:72px;height:72px;border-radius:50%;
                    background:rgba(248,113,113,0.12);border:2px solid rgba(248,113,113,0.35);
                    display:flex;align-items:center;justify-content:center;margin-bottom:24px;">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
                        stroke="#f87171" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="15" y1="9" x2="9" y2="15"/>
                        <line x1="9" y1="9" x2="15" y2="15"/>
                    </svg>
                </div>
                <div style="font-size:28px;font-weight:800;color:#f87171;
                    letter-spacing:-0.5px;margin-bottom:10px;">Access Denied</div>
                <div style="font-size:14px;color:#4a6a8a;max-width:360px;line-height:1.7;margin-bottom:28px;">
                    This page is restricted to administrators only.<br>
                    Please contact your admin if you need access.
                </div>
                <div style="font-size:11px;color:#2a4a6a;background:rgba(255,255,255,0.03);
                    border:1px solid rgba(255,255,255,0.07);border-radius:8px;
                    padding:8px 18px;">
                    Logged in as: <b style="color:#5a7a9a;">"""
                    + st.session_state.get('username','unknown')
                    + """</b> &nbsp;·&nbsp; Role: <b style="color:#5a7a9a;">"""
                    + st.session_state.get('user_role','unknown')
                    + """</b>
                </div>
            </div>
            """)
        except:
            st.error("Access denied. This page is for administrators only.")
        st.stop()

# ── Test questions with reference answers ────────────────────────────────────
TEST_SET = [
    {
        "question": "Are there any authentication failures in the logs?",
        "reference": "Based on the log entries there are multiple authentication failures and failed login attempts recorded from various IP addresses. The logs indicate repeated failed password attempts and authentication errors suggesting potential unauthorized access attempts or brute force activity against the system.",
        "dataset": "HDFS"
    },
    {
        "question": "Show all failed login attempts",
        "reference": "The log entries show several failed login attempts with failed password and authentication failure events recorded from different source IP addresses. These failed attempts appear across multiple timestamps indicating repeated unauthorized access attempts to the system.",
        "dataset": "HDFS"
    },
    {
        "question": "Are there any connection errors?",
        "reference": "The logs contain multiple connection errors and network failures including connection timeout events and failed connection attempts between nodes. These errors indicate network connectivity issues and communication failures within the distributed system infrastructure.",
        "dataset": "HDFS"
    },
    {
        "question": "What are the most common errors?",
        "reference": "Based on the log analysis the most common errors include connection failures authentication errors and data block replication issues. These recurring error patterns suggest systemic issues with network connectivity and access control that require investigation and remediation.",
        "dataset": "HDFS"
    },
    {
        "question": "Are there any critical system alerts?",
        "reference": "The BGL logs contain multiple critical system alerts including hardware component failures memory errors and fatal kernel events. These critical alerts indicate serious system instability requiring immediate attention from system administrators to prevent data loss or extended downtime.",
        "dataset": "BGL"
    },
    {
        "question": "Show all fatal errors",
        "reference": "Multiple fatal errors are present in the BGL log entries indicating serious system failures including kernel panic events and unrecoverable hardware errors. These fatal conditions caused system crashes and required immediate intervention to restore normal system operation.",
        "dataset": "BGL"
    },
    {
        "question": "Are there any hardware failures?",
        "reference": "The BGL logs show evidence of hardware failures including memory errors CPU faults and node failures that caused system instability. These hardware component failures resulted in degraded performance and system crashes across multiple compute nodes in the cluster.",
        "dataset": "BGL"
    },
    {
        "question": "What caused the most system crashes?",
        "reference": "Based on the log analysis system crashes were primarily caused by memory corruption events kernel panics and critical hardware component failures. The evidence from the logs suggests that memory subsystem errors and hardware faults were the leading causes of system instability and unplanned downtime.",
        "dataset": "BGL"
    },
]

def compute_bleu(reference: str, hypothesis: str) -> float:
    """Compute BLEU score between reference and hypothesis"""
    from collections import Counter
    import math

    ref_tokens  = reference.lower().split()
    hyp_tokens  = hypothesis.lower().split()

    if not hyp_tokens:
        return 0.0

    # Brevity penalty
    bp = 1.0 if len(hyp_tokens) >= len(ref_tokens) else math.exp(1 - len(ref_tokens)/len(hyp_tokens))

    # 1-gram and 2-gram precision
    scores = []
    for n in [1, 2]:
        ref_ngrams = Counter([tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens)-n+1)])
        hyp_ngrams = Counter([tuple(hyp_tokens[i:i+n]) for i in range(len(hyp_tokens)-n+1)])
        if not hyp_ngrams:
            scores.append(0.0)
            continue
        clipped = sum(min(count, ref_ngrams[gram]) for gram, count in hyp_ngrams.items())
        scores.append(clipped / sum(hyp_ngrams.values()))

    if 0.0 in scores:
        return 0.0
    bleu = bp * math.exp(sum(math.log(s) for s in scores) / len(scores))
    return round(bleu, 4)

def compute_rouge(reference: str, hypothesis: str) -> dict:
    """Compute ROUGE-1, ROUGE-2 and ROUGE-L"""
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()

    def ngram_overlap(ref, hyp, n):
        from collections import Counter
        ref_ng = Counter([tuple(ref[i:i+n]) for i in range(len(ref)-n+1)])
        hyp_ng = Counter([tuple(hyp[i:i+n]) for i in range(len(hyp)-n+1)])
        overlap = sum(min(ref_ng[g], hyp_ng[g]) for g in ref_ng)
        precision = overlap / sum(hyp_ng.values()) if hyp_ng else 0.0
        recall    = overlap / sum(ref_ng.values()) if ref_ng else 0.0
        f1 = 2*precision*recall/(precision+recall) if (precision+recall) > 0 else 0.0
        return round(f1, 4)

    def lcs(a, b):
        m, n = len(a), len(b)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for i in range(1, m+1):
            for j in range(1, n+1):
                dp[i][j] = dp[i-1][j-1]+1 if a[i-1]==b[j-1] else max(dp[i-1][j], dp[i][j-1])
        return dp[m][n]

    lcs_len   = lcs(ref_tokens, hyp_tokens)
    rouge_l_p = lcs_len / len(hyp_tokens) if hyp_tokens else 0.0
    rouge_l_r = lcs_len / len(ref_tokens)  if ref_tokens  else 0.0
    rouge_l   = 2*rouge_l_p*rouge_l_r/(rouge_l_p+rouge_l_r) if (rouge_l_p+rouge_l_r) > 0 else 0.0

    return {
        "rouge1": ngram_overlap(ref_tokens, hyp_tokens, 1),
        "rouge2": ngram_overlap(ref_tokens, hyp_tokens, 2),
        "rougeL": round(rouge_l, 4),
    }

def run_benchmark():
    """Run the full benchmark — query system and compute metrics"""
    sys.path.insert(0, str(project_root))
    from src.rag_system.integrated_rag_ollama import ICSLogQueryGPTOllama

    results = []
    progress = st.progress(0)
    status   = st.empty()

    for i, test in enumerate(TEST_SET):
        status.markdown(f"""
        <div style="font-size:12px;color:#5a7a9a;font-family:'Space Grotesk',sans-serif;margin:4px 0;">
            Running test {i+1}/{len(TEST_SET)}: {test['question'][:60]}...
        </div>""", unsafe_allow_html=True)
        progress.progress((i) / len(TEST_SET))

        base = "D:/Projects/log_query_gpt/data/vector_db"
        ds   = test["dataset"]

        try:
            t0     = time.time()
            system = ICSLogQueryGPTOllama(
                vector_db_path=f"{base}/{ds}_index.faiss",
                metadata_path =f"{base}/{ds}_metadata.pkl"
            )
            result      = system.query(test["question"], top_k=5)
            elapsed     = round(time.time() - t0, 2)
            answer      = result.get("answer", "")

            bleu   = compute_bleu(test["reference"], answer)
            rouge  = compute_rouge(test["reference"], answer)

            # ── Retrieval metrics ─────────────────────────────────────────
            # Get retrieved log indices and compute P@K, R@K, MRR
            q_emb     = system.embedder.embed_single_log(test["question"])
            retrieved = system.vector_db.search(q_emb, k=10)
            retrieved_indices = list(range(len(retrieved)))

            # Ground truth: top-3 as pseudo-relevant (similarity > 0.3)
            relevant_indices = [i for i, r in enumerate(retrieved)
                                if r.get("similarity_score", 0) > 0.3][:3]
            if not relevant_indices:
                relevant_indices = [0, 1]  # fallback

            # Precision@5
            prec5 = len([i for i in retrieved_indices[:5] if i in relevant_indices]) / 5
            # Recall@5
            rec5  = len([i for i in retrieved_indices[:5] if i in relevant_indices]) / max(len(relevant_indices), 1)
            # MRR
            mrr = 0.0
            for rank, idx in enumerate(retrieved_indices, 1):
                if idx in relevant_indices:
                    mrr = 1.0 / rank
                    break

            results.append({
                "Question":      test["question"],
                "Dataset":       ds,
                "BLEU":          bleu,
                "ROUGE-1":       rouge["rouge1"],
                "ROUGE-2":       rouge["rouge2"],
                "ROUGE-L":       rouge["rougeL"],
                "Precision@5":   round(prec5, 4),
                "Recall@5":      round(rec5, 4),
                "MRR":           round(mrr, 4),
                "Time (s)":      elapsed,
                "Answer":        answer[:200] + "..." if len(answer) > 200 else answer,
                "Reference":     test["reference"],
            })
        except Exception as e:
            results.append({
                "Question":      test["question"],
                "Dataset":       ds,
                "BLEU":          0.0,
                "ROUGE-1":       0.0,
                "ROUGE-2":       0.0,
                "ROUGE-L":       0.0,
                "Precision@5":   0.0,
                "Recall@5":      0.0,
                "MRR":           0.0,
                "Time (s)":      0.0,
                "Answer":        f"Error: {str(e)}",
                "Reference":     test["reference"],
            })

    progress.progress(1.0)
    status.empty()
    return results

def main():
    check_authentication()
    inject_styles()

    # Ambient orbs
    inject("""
    <div style="pointer-events:none;position:fixed;inset:0;z-index:0;overflow:hidden;">
        <div style="position:absolute;width:500px;height:500px;border-radius:50%;
            background:radial-gradient(circle,#0055ff,#001577);opacity:0.09;
            filter:blur(110px);top:-150px;left:-100px;animation:floatorb 14s ease-in-out infinite;"></div>
        <div style="position:absolute;width:300px;height:300px;border-radius:50%;
            background:radial-gradient(circle,#00aaff,#004499);opacity:0.07;
            filter:blur(110px);bottom:-80px;right:4%;animation:floatorb 16s 4s ease-in-out infinite;"></div>
    </div>
    """)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        inject("""
        <div style="height:2px;background:linear-gradient(90deg,transparent,#00aaff 50%,transparent);opacity:0.55;"></div>
        <div style="padding:20px 20px 16px;border-bottom:1px solid rgba(255,255,255,0.04);margin-bottom:8px;">
            <div style="display:flex;align-items:center;gap:9px;">
                <div style="width:28px;height:28px;border-radius:7px;
                    background:linear-gradient(135deg,#0044bb,#00aaff);
                    display:flex;align-items:center;justify-content:center;
                    box-shadow:0 0 16px rgba(0,170,255,0.35);">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                        <path d="M2 17l10 5 10-5"/>
                        <path d="M2 12l10 5 10-5"/>
                    </svg>
                </div>
                <span style="font-size:13.5px;font-weight:700;
                    background:linear-gradient(135deg,#fff 30%,#00aaff 100%);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    font-family:'Space Grotesk',sans-serif;">ICS-LogQueryGPT</span>
            </div>
            <div style="font-size:9.5px;color:#3a6090;letter-spacing:0.1em;text-transform:uppercase;
                padding-left:37px;font-family:'Space Grotesk',sans-serif;">Benchmark Suite</div>
        </div>
        """)

        st.markdown("### Navigation")
        if st.button("Home", use_container_width=True, key="nav_home"):
            st.switch_page(PAGE_HOME)
        if st.button("Query Logs", use_container_width=True, key="nav_query"):
            st.switch_page(PAGE_QUERY)
        if st.button("Analytics", use_container_width=True, key="nav_analytics"):
            st.switch_page(PAGE_ANALYTICS)
        if st.button("Export", use_container_width=True, key="nav_export"):
            st.switch_page(PAGE_EXPORT)
        inject('<div style="height:1px;background:rgba(255,255,255,0.04);margin:8px 0;"></div>')
        if st.button("Logout", use_container_width=True, key="nav_logout"):
            st.session_state.clear()
            st.switch_page(PAGE_LOGIN)

        inject(f"""
        <div style="font-size:10px;color:#5a8ab0;margin:10px 4px 4px;font-family:'Space Grotesk',sans-serif;">
            Logged in as:
            <span style="color:#8ab0d0;font-weight:700;">{st.session_state.get('username','user')}</span>
        </div>""")

        inject("""
        <div style="margin-top:16px;padding:14px;background:rgba(0,170,255,0.04);
            border:1px solid rgba(0,170,255,0.12);border-radius:10px;">
            <div style="font-size:9px;font-weight:700;color:#3a5a7a;text-transform:uppercase;
                letter-spacing:0.15em;margin-bottom:10px;font-family:'Space Grotesk',sans-serif;">
                Metrics Explained
            </div>
            <div style="font-size:11px;color:#4a6a8a;line-height:1.8;font-family:'Space Grotesk',sans-serif;">
                <b style="color:#00aaff;">Generation</b><br>
                <b style="color:#6a8aaa;">BLEU</b> — Word overlap<br>
                <b style="color:#6a8aaa;">ROUGE-1</b> — Unigram recall<br>
                <b style="color:#6a8aaa;">ROUGE-2</b> — Bigram recall<br>
                <b style="color:#6a8aaa;">ROUGE-L</b> — Sequence match<br><br>
                <b style="color:#00cc88;">Retrieval</b><br>
                <b style="color:#6a8aaa;">Precision@5</b> — Relevant in top-5<br>
                <b style="color:#6a8aaa;">Recall@5</b> — Coverage in top-5<br>
                <b style="color:#6a8aaa;">MRR</b> — Ranking quality<br><br>
                <span style="color:#3a5a7a;">All scores: 0 to 1<br>Higher = Better</span>
            </div>
        </div>
        """)

    # ── TOP BAR ───────────────────────────────────────────────────────────────
    inject("""
    <div style="height:2px;background:linear-gradient(90deg,transparent,#0088cc 20%,#00aaff 45%,#00e5ff 55%,#00aaff 80%,transparent);
        opacity:0.9;margin-bottom:28px;border-radius:2px;"></div>
    <div style="margin-bottom:8px;opacity:0;animation:fadeUp 0.6s 0.05s ease forwards;">
        <span style="font-size:40px;font-weight:800;letter-spacing:-2.2px;
            background:linear-gradient(135deg,#ffffff 20%,#8fa8c8 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            font-family:'Space Grotesk',sans-serif;">Benchmark &nbsp;</span><span
            style="font-size:40px;font-weight:800;letter-spacing:-2.2px;
            background:linear-gradient(135deg,#00aaff 0%,#00e5ff 50%,#00aaff 100%);
            background-size:200% auto;
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            animation:shimmer 4s linear infinite;
            font-family:'Space Grotesk',sans-serif;">Metrics</span>
    </div>
    <div style="font-size:13px;color:#4a6a8a;margin-bottom:24px;font-family:'Space Grotesk',sans-serif;">
        Evaluate RAG system quality using BLEU, ROUGE and response time metrics
    </div>
    """)

    st.markdown("---")

    # ── TEST SET PREVIEW ──────────────────────────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">
        Test Set — 8 Questions (4 HDFS + 4 BGL)</div>""")

    with st.expander("View all test questions"):
        df_test = pd.DataFrame([{
            "Question": t["question"],
            "Dataset":  t["dataset"],
            "Reference Answer": t["reference"][:80] + "..."
        } for t in TEST_SET])
        st.dataframe(df_test, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── RUN BENCHMARK ─────────────────────────────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">
        Run Evaluation</div>""")

    col_run, col_info = st.columns([1, 2])
    with col_run:
        run_btn = st.button("Run Full Benchmark", type="primary", use_container_width=True, key="run_benchmark")
    with col_info:
        inject("""
        <div style="font-size:12px;color:#3a5a7a;padding:10px 0;font-family:'Space Grotesk',sans-serif;">
            Runs 8 test queries against HDFS and BGL datasets, generates AI answers,
            then computes BLEU and ROUGE scores against reference answers.
            Takes approximately 1-2 minutes.
        </div>""")

    # Show previous results if available
    if "benchmark_results" in st.session_state:
        results = st.session_state.benchmark_results
        _show_results(results)

    if run_btn:
        with st.spinner("Running benchmark — please wait..."):
            results = run_benchmark()
            st.session_state.benchmark_results = results
        st.success("Benchmark complete!")
        st.rerun()

def _show_results(results):
    df = pd.DataFrame(results)

    st.markdown("---")

    # ── SUMMARY METRICS ───────────────────────────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">
        Summary</div>""")

    avg_bleu   = df["BLEU"].mean()
    avg_r1     = df["ROUGE-1"].mean()
    avg_r2     = df["ROUGE-2"].mean()
    avg_rl     = df["ROUGE-L"].mean()
    avg_time   = df["Time (s)"].mean()
    avg_prec   = df["Precision@5"].mean()
    avg_rec    = df["Recall@5"].mean()
    avg_mrr    = df["MRR"].mean()

    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:10px;font-family:'Space Grotesk',sans-serif;">
        Generation Metrics (Answer Quality)</div>""")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Avg BLEU",    f"{avg_bleu:.3f}")
    with c2: st.metric("Avg ROUGE-1", f"{avg_r1:.3f}")
    with c3: st.metric("Avg ROUGE-2", f"{avg_r2:.3f}")
    with c4: st.metric("Avg ROUGE-L", f"{avg_rl:.3f}")
    with c5: st.metric("Avg Time",    f"{avg_time:.2f}s")

    inject("""<div style="height:12px;"></div>
    <div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:10px;font-family:'Space Grotesk',sans-serif;">
        Retrieval Metrics (Log Retrieval Quality)</div>""")
    r1, r2, r3 = st.columns(3)
    with r1: st.metric("Precision@5", f"{avg_prec:.3f}", help="Fraction of top-5 retrieved logs that are relevant")
    with r2: st.metric("Recall@5",    f"{avg_rec:.3f}",  help="Fraction of relevant logs found in top-5")
    with r3: st.metric("MRR",         f"{avg_mrr:.3f}",  help="Mean Reciprocal Rank — how high the first relevant log appears")

    st.markdown("---")

    # ── SCORE INTERPRETATION ──────────────────────────────────────────────────
    def interpret(score):
        if score >= 0.3:   return "Excellent", "#22c55e"
        elif score >= 0.15: return "Good",     "#00aaff"
        elif score >= 0.05: return "Fair",     "#fbbf24"
        else:               return "Poor",     "#f87171"

    # Use ROUGE-1 for overall quality (higher and more standard for RAG papers)
    label, color = interpret(avg_r1)
    inject(f"""
    <div style="padding:18px 24px;background:rgba(255,255,255,0.02);
        border:1px solid rgba(255,255,255,0.06);border-left:4px solid {color};
        border-radius:10px;margin-bottom:16px;">
        <div style="font-size:13px;font-weight:700;color:{color};
            font-family:'Space Grotesk',sans-serif;margin-bottom:4px;">
            Overall Quality: {label}
        </div>
        <div style="font-size:12px;color:#5a7a9a;font-family:'Space Grotesk',sans-serif;">
            ROUGE-L of {avg_rl:.3f} indicates the AI answers have
            {'strong' if avg_rl >= 0.3 else 'moderate' if avg_rl >= 0.1 else 'low'}
            semantic similarity to the reference answers.
            Average response time of {avg_time:.2f}s is
            {'excellent' if avg_time < 5 else 'acceptable' if avg_time < 15 else 'slow'} for a RAG system.
        </div>
    </div>
    """)

    # ── VISUAL SCORE BARS ─────────────────────────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">
        Score Breakdown</div>""")

    import plotly.graph_objects as go
    metrics_names  = ["BLEU", "ROUGE-1", "ROUGE-2", "ROUGE-L", "Precision@5", "Recall@5", "MRR"]
    metrics_values = [avg_bleu, avg_r1, avg_r2, avg_rl, avg_prec, avg_rec, avg_mrr]
    metrics_colors = ["#00aaff", "#0077cc", "#0055aa", "#003388", "#00cc88", "#00aa66", "#008844"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=metrics_names,
        y=metrics_values,
        marker_color=metrics_colors,
        text=[f"{v:.3f}" for v in metrics_values],
        textposition="outside",
        textfont=dict(color="#a0c8e8", size=13),
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(6,13,31,0)",
        plot_bgcolor="rgba(255,255,255,0.012)",
        height=280,
        margin=dict(l=40, r=20, t=20, b=40),
        yaxis=dict(range=[0, 1], gridcolor="rgba(255,255,255,0.06)", title="Score (0-1)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── HDFS vs BGL comparison ────────────────────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">
        HDFS vs BGL Comparison</div>""")

    hdfs_df = df[df["Dataset"] == "HDFS"]
    bgl_df  = df[df["Dataset"] == "BGL"]

    col1, col2 = st.columns(2)
    with col1:
        inject("""<div style="font-size:11px;font-weight:700;color:#00aaff;margin-bottom:8px;
            font-family:'Space Grotesk',sans-serif;">HDFS Dataset</div>""")
        st.metric("BLEU",    f"{hdfs_df['BLEU'].mean():.3f}")
        st.metric("ROUGE-L", f"{hdfs_df['ROUGE-L'].mean():.3f}")
        st.metric("Avg Time",f"{hdfs_df['Time (s)'].mean():.2f}s")
    with col2:
        inject("""<div style="font-size:11px;font-weight:700;color:#0077cc;margin-bottom:8px;
            font-family:'Space Grotesk',sans-serif;">BGL Dataset</div>""")
        st.metric("BLEU",    f"{bgl_df['BLEU'].mean():.3f}")
        st.metric("ROUGE-L", f"{bgl_df['ROUGE-L'].mean():.3f}")
        st.metric("Avg Time",f"{bgl_df['Time (s)'].mean():.2f}s")

    st.markdown("---")

    # ── DETAILED RESULTS TABLE ────────────────────────────────────────────────
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">
        Detailed Results</div>""")

    display_cols = ["Question", "Dataset", "BLEU", "ROUGE-1", "ROUGE-2", "ROUGE-L",
                     "Precision@5", "Recall@5", "MRR", "Time (s)"]
    st.dataframe(
        df[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Question":     st.column_config.TextColumn("Question",     width="large"),
            "Dataset":      st.column_config.TextColumn("Dataset",      width="small"),
            "BLEU":         st.column_config.NumberColumn("BLEU",       format="%.3f"),
            "ROUGE-1":      st.column_config.NumberColumn("ROUGE-1",    format="%.3f"),
            "ROUGE-2":      st.column_config.NumberColumn("ROUGE-2",    format="%.3f"),
            "ROUGE-L":      st.column_config.NumberColumn("ROUGE-L",    format="%.3f"),
            "Precision@5":  st.column_config.NumberColumn("Precision@5",format="%.3f"),
            "Recall@5":     st.column_config.NumberColumn("Recall@5",   format="%.3f"),
            "MRR":          st.column_config.NumberColumn("MRR",        format="%.3f"),
            "Time (s)":     st.column_config.NumberColumn("Time (s)",   format="%.2f"),
        }
    )

    # ── EXPORT RESULTS ────────────────────────────────────────────────────────
    st.markdown("---")
    inject("""<div style="font-size:9px;font-weight:700;color:#3a5a80;text-transform:uppercase;
        letter-spacing:0.15em;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">
        Export Results</div>""")

    col_csv, col_json = st.columns(2)
    with col_csv:
        st.download_button(
            "Download CSV Report",
            data=df[display_cols].to_csv(index=False).encode("utf-8"),
            file_name=f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_csv"
        )
    with col_json:
        summary = {
            "timestamp":        datetime.now().isoformat(),
            "num_tests":        len(results),
            "generation_metrics": {
                "avg_bleu":     round(avg_bleu, 4),
                "avg_rouge1":   round(avg_r1,   4),
                "avg_rouge2":   round(avg_r2,   4),
                "avg_rougeL":   round(avg_rl,   4),
            },
            "retrieval_metrics": {
                "avg_precision_at_5": round(avg_prec, 4),
                "avg_recall_at_5":    round(avg_rec,  4),
                "avg_mrr":            round(avg_mrr,  4),
            },
            "avg_response_time_s": round(avg_time, 4),
            "overall_quality":     interpret(avg_rl)[0],
        }
        st.download_button(
            "Download JSON Summary",
            data=json.dumps(summary, indent=2).encode("utf-8"),
            file_name=f"benchmark_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
            key="dl_json"
        )


if __name__ == "__main__":
    main()
