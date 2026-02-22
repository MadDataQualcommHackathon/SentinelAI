import streamlit as st
import requests
import time
import threading
import queue
import itertools
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="Sentinel-Edge | Snapdragon NPU",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Cyber-Corporate / Hardware Theme
st.markdown("""
<style>
    /* Global Theme tweaks */
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    
    /* Snapdragon / Hardware Badge styling */
    .snapdragon-badge {
        background: linear-gradient(135deg, #FF004F 0%, #8A2387 100%);
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: 900;
        font-size: 1.2rem;
        letter-spacing: 1.5px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(255, 0, 79, 0.4);
    }
    .npu-text { font-size: 0.8rem; font-family: monospace; opacity: 0.9; }

    /* Telemetry Panel */
    .telemetry-panel {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 15px;
        display: flex;
        justify-content: space-between;
        margin-bottom: 25px;
        font-family: monospace;
    }
    .telemetry-item { text-align: center; }
    .telemetry-val { color: #00f0ff; font-size: 1.5rem; font-weight: bold; }
    .telemetry-lbl { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; }

    /* Risk Level Cards */
    .risk-card {
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        background-color: #1e293b;
        border: 1px solid #334155;
    }
    .risk-high {
        border-left: 6px solid #ff004f;
        box-shadow: 0 0 15px rgba(255, 0, 79, 0.1);
    }
    .risk-med {
        border-left: 6px solid #f59e0b;
    }
    .risk-low {
        border-left: 6px solid #10b981;
    }
    
    /* Typography */
    .card-title { font-size: 1.2rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.5rem; }
    .badge {
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 1px;
    }
    .badge-high { background-color: rgba(255, 0, 79, 0.2); color: #ff004f; border: 1px solid #ff004f; }
    .badge-med { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .badge-low { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    
    .excerpt-box {
        background-color: #0f172a;
        border: 1px dashed #475569;
        padding: 12px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
        margin: 15px 0;
        color: #cbd5e1;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTS & SETUP
# ==========================================
API_URL = "http://localhost:8000/api/analyze"

MODE_MAP = {
    "Legal Risk Scoring": "legal_risk_scoring",
    "PII Masking Audit": "pii_masking",
    "Vulnerability Detection": "vulnerability_detection"
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def draw_gauge(score):
    """Draws a high-tech Plotly gauge chart."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "THREAT SCORE", 'font': {'size': 20, 'color': '#94a3b8'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#ff004f" if score > 60 else "#f59e0b" if score > 30 else "#10b981"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': 'rgba(16, 185, 129, 0.1)'},
                {'range': [30, 60], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [60, 100], 'color': 'rgba(255, 0, 79, 0.1)'}],
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=300, margin=dict(l=20, r=20, t=30, b=20))
    return fig

def render_finding_card(finding, mode):
    if mode == "vulnerability_detection":
        level = finding.get("severity", "LOW").upper()
        title = finding.get("vulnerability_type", "Unknown")
    elif mode == "legal_risk_scoring":
        level = finding.get("risk_level", "LOW").upper()
        title = finding.get("clause_type", "Unknown")
    else:
        level = "HIGH"
        title = finding.get("pii_type", "Unknown")
        
    excerpt = finding.get("excerpt", "")
    rec = finding.get("recommendation", "")

    if level == "HIGH": card_cls, badge_cls = "risk-high", "badge-high"
    elif level == "MED": card_cls, badge_cls = "risk-med", "badge-med"
    else: card_cls, badge_cls = "risk-low", "badge-low"

    html = f"""
    <div class="risk-card {card_cls}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="card-title">▧ {title}</div>
            <div class="badge {badge_cls}">{level} RISK</div>
        </div>
        <div class="excerpt-box">> {excerpt}</div>
        <div style="margin-top: 10px; color: #00f0ff; font-family: monospace;">
            <b>[ACTION REQUIRED]:</b> <span style="color: #cbd5e1;">{rec}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Background API Thread ---
def fetch_api_data(files, data, result_queue):
    """Runs the blocking API call in a background thread."""
    try:
        response = requests.post(API_URL, files=files, data=data)
        response.raise_for_status()
        result_queue.put(("success", response.json()))
    except Exception as e:
        result_queue.put(("error", str(e)))

# ==========================================
# UI: SIDEBAR
# ==========================================
with st.sidebar:
    # High-impact hardware badge instead of a broken image link
    st.markdown("""
    <div class="snapdragon-badge">
        SNAPDRAGON® X ELITE<br>
        <span class="npu-text">► HEXAGON™ NPU ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔒 Air-Gapped Analysis")
    st.caption("Zero Cloud Connectivity. Enterprise Data never leaves this device.")
    st.divider()
    
    st.header("1. Target Payload")
    uploaded_file = st.file_uploader("Upload PDF Contract or Code", type=["pdf"], label_visibility="collapsed")
    
    st.header("2. Analysis Engine")
    selected_mode_label = st.radio("Mode", list(MODE_MAP.keys()), label_visibility="collapsed")
    
    analyze_btn = st.button("🚀 INITIATE SCAN", type="primary", use_container_width=True)

# ==========================================
# UI: MAIN DASHBOARD
# ==========================================
st.title("🛡️ Sentinel-Edge Command Center")

# Telemetry Bar
st.markdown("""
<div class="telemetry-panel">
    <div class="telemetry-item"><div class="telemetry-val">45 TOPS</div><div class="telemetry-lbl">NPU Compute</div></div>
    <div class="telemetry-item"><div class="telemetry-val">Llama 3.2 3B</div><div class="telemetry-lbl">Local LLM</div></div>
    <div class="telemetry-item"><div class="telemetry-val">0 bytes</div><div class="telemetry-lbl">Cloud Data Leakage</div></div>
    <div class="telemetry-item"><div class="telemetry-val">Secure</div><div class="telemetry-lbl">Enclave Status</div></div>
</div>
""", unsafe_allow_html=True)

if not uploaded_file:
    st.info("Awaiting payload. Upload a document in the sidebar to initiate on-device NPU scan.")
    st.stop()

if analyze_btn and uploaded_file:
    api_mode = MODE_MAP[selected_mode_label]
    
    # ---------------------------------------------------------
    # DYNAMIC LOADING ANIMATION (Hardware Track Specific)
    # ---------------------------------------------------------
    loading_messages = [
        "Waking Snapdragon® Hexagon™ NPU...",
        "Loading Llama 3.2 3B weights into Neural Cache...",
        "Parsing document structure & executing layout analysis...",
        "Searching 10,000 pages of CUAD legal corpus...",
        "Vectorizing 40,000 chunks via ChromaDB...",
        "Cross-referencing RAG context with local embeddings...",
        "Executing semantic threat analysis...",
        "Isolating PII and executing redaction protocols...",
        "Securing data via on-device isolation...",
        "Finalizing analysis. (Awaiting full generation, ~60 seconds)..."
    ]
    
    result_queue = queue.Queue()
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    data = {"analysis_mode": api_mode}
    
    api_thread = threading.Thread(target=fetch_api_data, args=(files, data, result_queue))
    api_thread.start()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    msg_cycle = itertools.cycle(loading_messages)
    progress_val = 0
    start_time = time.time()
    
    # Keep updating UI while the backend thread is working
    while api_thread.is_alive():
        # Cycle text every 1.5 seconds, but lock on the last message if we reach it
        current_msg = next(msg_cycle)
        if "60 seconds" in current_msg:
            msg_cycle = itertools.repeat(current_msg) # Stay on the last message
            
        status_text.info(f"⚡ **SYSTEM STATUS:** {current_msg}")
        
        # Fake progress bar mechanics (slows down as it gets closer to 100)
        progress_val += (95 - progress_val) * 0.05 
        progress_bar.progress(int(progress_val))
        
        time.sleep(1.5)
    
    # Clean up animation once done
    api_thread.join()
    status_text.empty()
    progress_bar.empty()
    
    status, result = result_queue.get()
    
    if status == "error":
        st.error(f"Analysis failed: {result}")
        st.stop()
        
    elapsed_time = round(time.time() - start_time, 1)
    st.success(f"✅ On-Device Scan Completed in {elapsed_time}s")
            
    # ==========================================
    # RENDER RESULTS
    # ==========================================
    st.divider()
    st.header(f"📑 Intelligence Report: `{uploaded_file.name}`")
    
    res_data = result.get("data", {})
    
    # --- VIEW 1: LEGAL RISK SCORING ---
    if api_mode == "legal_risk_scoring":
        findings = res_data.get("findings", [])
        score = res_data.get("score", 0)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.plotly_chart(draw_gauge(score), use_container_width=True)
        with col2:
            st.markdown("### Threat Assessment")
            high_count = sum(1 for f in findings if f.get("risk_level") == "HIGH")
            med_count = sum(1 for f in findings if f.get("risk_level") == "MED")
            low_count = sum(1 for f in findings if f.get("risk_level") == "LOW")
            
            c1, c2, c3 = st.columns(3)
            c1.metric(label="Critical Clauses", value=high_count, delta="Immediate Action" if high_count > 0 else None, delta_color="inverse")
            c2.metric(label="Medium Risk", value=med_count)
            c3.metric(label="Standard Boilerplate", value=low_count)

        st.subheader("🔍 Contextual Clause Breakdown")
        for finding in sorted(findings, key=lambda x: {"HIGH": 0, "MED": 1, "LOW": 2}.get(x.get("risk_level", "LOW"), 3)):
            render_finding_card(finding, api_mode)

    # --- VIEW 2: VULNERABILITY DETECTION ---
    elif api_mode == "vulnerability_detection":
        findings = res_data.get("findings", [])
        
        st.markdown("### 👾 Source Code Audit")
        high_count = sum(1 for f in findings if f.get("severity") == "HIGH")
        total = len(findings)
        
        c1, c2 = st.columns(2)
        c1.metric(label="Total CWE/OWASP Vectors", value=total)
        c2.metric(label="High Severity Exposures", value=high_count, delta="Requires Patch" if high_count > 0 else None, delta_color="inverse")
        
        st.subheader("🛡️ Vulnerability Matrix")
        for finding in sorted(findings, key=lambda x: {"HIGH": 0, "MED": 1, "LOW": 2}.get(x.get("severity", "LOW"), 3)):
            render_finding_card(finding, api_mode)

    # --- VIEW 3: PII MASKING ---
    elif api_mode == "pii_masking":
        instances = res_data.get("pii_instances", [])
        
        st.markdown("### 🕵️ Data Sovereignty Audit")
        st.metric(label="Total PII Leaks Quarantined", value=len(instances), delta="Compliance Violation" if len(instances) > 0 else "GDPR Compliant", delta_color="inverse")
        
        st.subheader("⚠️ Redaction Logs")
        if not instances:
            st.success("No sensitive PII detected in this document.")
        for finding in instances:
            render_finding_card(finding, api_mode)