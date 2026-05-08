import streamlit as st
import pandas as pd
import json
import os
import sys
import plotly.express as px
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentstress.data.local_ledger import LocalLedger
from agentstress.config import Config

# --- HIGH-END CYBER AUDIT THEME ---
st.set_page_config(page_title="AGENTSTRESS // AUDIT_OS", page_icon="📟", layout="wide")

def apply_custom_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Main background */
        .stApp {
            background-color: #05070a;
            color: #e0e0e0;
            font-family: 'JetBrains Mono', monospace;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #0a0e14;
            border-right: 1px solid #1d2b3a;
        }

        /* Metric Cards */
        [data-testid="stMetric"] {
            background: rgba(29, 43, 58, 0.4);
            border: 1px solid #1d2b3a;
            padding: 20px;
            border-radius: 4px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover {
            border-color: #00ff41;
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
        }

        /* Status Box */
        .status-card {
            padding: 24px;
            border-radius: 4px;
            text-align: center;
            font-weight: bold;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: 1px solid;
            margin-bottom: 20px;
        }
        .secure-card {
            background: rgba(0, 255, 65, 0.05);
            color: #00ff41;
            border-color: #00ff41;
            box-shadow: inset 0 0 20px rgba(0, 255, 65, 0.1);
        }
        .danger-card {
            background: rgba(255, 62, 62, 0.05);
            color: #ff3e3e;
            border-color: #ff3e3e;
            box-shadow: inset 0 0 20px rgba(255, 62, 62, 0.1);
        }

        /* Dataframe styling */
        .stDataFrame {
            border: 1px solid #1d2b3a;
        }

        /* Headers */
        h1, h2, h3 {
            color: #ffffff !important;
            font-weight: 700 !important;
            letter-spacing: -1px;
        }
        
        .terminal-header {
            border-bottom: 2px solid #1d2b3a;
            padding-bottom: 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .tag {
            background: #1d2b3a;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            color: #8892b0;
        }
        
        /* Button Styling */
        .stButton>button {
            background-color: transparent;
            color: #00ff41;
            border: 1px solid #00ff41;
            border-radius: 2px;
            text-transform: uppercase;
            font-family: 'JetBrains Mono', monospace;
            padding: 10px 24px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #00ff41;
            color: #05070a;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
def load_ledger_data():
    ledger_path = "data/evaluation_ledger.jsonl"
    if not os.path.exists(ledger_path): return pd.DataFrame()
    data = []
    with open(ledger_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            data.append({
                "TIMESTAMP": datetime.fromtimestamp(entry["timestamp"]).strftime('%Y-%m-%d %H:%M:%S'),
                "AGENT_ID": entry["data"].get("agent_id", "UNKNOWN"),
                "SCORE": entry["data"].get("score", 0),
                "FAILURE_MODE": entry["data"].get("judgment", {}).get("failure_mode") if "judgment" in entry["data"] else entry["data"].get("failure_classification", {}).get("failure_mode"),
                "CERT_HASH": entry["signature"][:12].upper()
            })
    return pd.DataFrame(data)

# Health Check Endpoint (For Deployment)
if "health" in st.query_params:
    st.write('{"status": "healthy"}')
    st.stop()


# --- EXECUTION ---
apply_custom_theme()

# Custom Header
st.markdown("""
    <div class="terminal-header">
        <div>
            <h1 style="margin:0;">AGENTSTRESS // <span style="color:#00ff41;">AUDIT_OS</span></h1>
            <p style="color:#8892b0; margin:0;">INDUSTRIAL-GRADE RELIABILITY CERTIFICATION ENGINE</p>
        </div>
        <div class="tag">V1.0.4_STABLE // SYSTEM_ONLINE</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### `CONTROL_CENTER`")
    if st.button("INITIATE_STRESS_TEST", use_container_width=True):
        with st.spinner("EXECUTING_PROTOCOL..."):
            import subprocess
            # Use sys.executable for cross-platform reliability
            subprocess.run([sys.executable, "agentstress/experiments/native_pilot.py"])
            st.rerun()
    
    st.divider()
    st.markdown("### `SYSTEM_SPECS`")
    st.code("ENCLAVE: READY\nCRYPT: RSA_4096\nHASH: SHA_256\nAUTH: LOCAL_LEDGER", language="makefile")
    st.divider()
    st.caption("© 2026 AGENTSTRESS CORE")

# Main Content
df = load_ledger_data()

if df.empty:
    st.info("NO_DATA_FOUND: WAITING FOR FIRST CERTIFICATION...")
else:
    # Top Row: Security Status & Metrics
    ledger = LocalLedger()
    is_secure = ledger.verify_ledger()
    
    m1, m2, m3 = st.columns([1, 1, 2])
    with m1:
        st.metric("AUDITS_TOTAL", len(df))
    with m2:
        st.metric("AVG_RELIABILITY", f"{df['SCORE'].mean():.1f}%")
    with m3:
        if is_secure:
            st.markdown('<div class="status-card secure-card">🛡️ SYSTEM_LEDGER: AUTHENTIC</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-card danger-card">⚠️ SYSTEM_LEDGER: COMPROMISED</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Second Row: Visual Analytics
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### `FAILURE_VECTORS`")
        fig = px.pie(df, names="FAILURE_MODE", hole=0.7, 
                     color_discrete_sequence=['#00ff41', '#1d2b3a', '#ff3e3e', '#8892b0'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          font_color='#e0e0e0', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.markdown("### `AGENT_LEADERBOARD`")
        leaderboard = df.groupby("AGENT_ID")["SCORE"].mean().reset_index()
        fig = px.bar(leaderboard, x="AGENT_ID", y="SCORE", color="SCORE",
                     color_continuous_scale=['#ff3e3e', '#00ff41'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          font_color='#e0e0e0')
        st.plotly_chart(fig, use_container_width=True)

    # Bottom Row: Ledger
    st.markdown("### `CERTIFIED_AUDIT_TRAIL`")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)

st.markdown("""
    <div style="text-align:right; color:#1d2b3a; font-size:0.7rem; margin-top:50px;">
        RUNNING_ON_ENCLAVE_SIMULATOR_V1
    </div>
""", unsafe_allow_html=True)
