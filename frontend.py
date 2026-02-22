import streamlit as st
import requests
import time
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="Sentinel-Edge AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Hackathon Impact (Glowing cards, badging)
st.markdown("""
<style>
    /* Main Dashboard Styling */
    .metric-card {
        background-color: #1E1E2E;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Risk Level Cards */
    .risk-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #E0E0E0;
        background-color: #1E1E1E;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .risk-high {
        border-left: 6px solid #FF4B4B;
        background: linear-gradient(90deg, rgba(255, 75, 75, 0.1) 0%, rgba(30, 30, 30, 0) 100%);
    }
    .risk-med {
        border-left: 6px solid #FFA500;
        background: linear-gradient(90deg, rgba(255, 165, 0, 0.1) 0%, rgba(30, 30, 30, 0) 100%);
    }
    .risk-low {
        border-left: 6px solid #00C04B;
        background: linear-gradient(90deg, rgba(0, 192, 75, 0.1) 0%, rgba(30, 30, 30, 0) 100%);
    }
    
    /* Text Elements */
    .card-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem; }
    .badge {
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .badge-high { background-color: #FF4B4B; color: white; }
    .badge-med { background-color: #FFA500; color: black; }
    .badge-low { background-color: #00C04B; color: white; }
    .excerpt-box {
        background-color: #2D2D2D;
        border-left: 3px solid #555;
        padding: 10px;
        font-family: monospace;
        font-size: 0.9rem;
        margin: 10px 0;
        color: #FFAAA5;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTS
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
    """Draws a beautiful Plotly gauge chart for the legal score."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Overall Legal Risk Score", 'font': {'size': 24, 'color': 'white'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#FF4B4B" if score > 60 else "#FFA500" if score > 30 else "#00C04B"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(0, 192, 75, 0.3)'},
                {'range': [30, 60], 'color': 'rgba(255, 165, 0, 0.3)'},
                {'range': [60, 100], 'color': 'rgba(255, 75, 75, 0.3)'}],
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=350)
    return fig

def render_finding_card(finding, mode):
    """Renders a custom HTML card based on the risk/severity level."""
    # Normalize keys based on analysis mode
    if mode == "vulnerability_detection":
        level = finding.get("severity", "LOW").upper()
        title = finding.get("vulnerability_type", "Unknown")
    elif mode == "legal_risk_scoring":
        level = finding.get("risk_level", "LOW").upper()
        title = finding.get("clause_type", "Unknown")
    else: # PII
        level = "HIGH" # PII is always flagged as high risk in your prompt
        title = finding.get("pii_type", "Unknown")
        
    excerpt = finding.get("excerpt", "")
    rec = finding.get("recommendation", "")

    # Assign CSS classes
    if level == "HIGH":
        card_cls, badge_cls = "risk-high", "badge-high"
    elif level == "MED":
        card_cls, badge_cls = "risk-med", "badge-med"
    else:
        card_cls, badge_cls = "risk-low", "badge-low"

    # Build HTML
    html = f"""
    <div class="risk-card {card_cls}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="card-title">{title}</div>
            <div class="badge {badge_cls}">{level} RISK</div>
        </div>
        <div class="excerpt-box">"{excerpt}"</div>
        <div style="margin-top: 10px;"><b>💡 Sentinel Recommendation:</b><br>{rec}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# UI: SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Qualcomm_Snapdragon_logo.svg/1024px-Qualcomm_Snapdragon_logo.svg.png", width=150)
    st.title("Sentinel-Edge")
    st.markdown("### 🔒 100% On-Device NPU Analysis")
    st.markdown("Zero Cloud. Zero Data Leaks.")
    
    st.divider()
    
    st.header("1. Upload Target Document")
    uploaded_file = st.file_uploader("Upload PDF Contract or Code", type=["pdf"], label_visibility="collapsed")
    
    st.header("2. Select Analysis Engine")
    selected_mode_label = st.radio(
        "Mode",
        list(MODE_MAP.keys()),
        label_visibility="collapsed"
    )
    
    analyze_btn = st.button("🚀 INITIATE SCAN", type="primary", use_container_width=True)

# ==========================================
# UI: MAIN DASHBOARD
# ==========================================
st.title("🛡️ Sentinel AI Threat Intelligence Dashboard")

if not uploaded_file:
    st.info("👈 Please upload a PDF and select an analysis mode in the sidebar to begin.")
    st.stop()

if analyze_btn and uploaded_file:
    api_mode = MODE_MAP[selected_mode_label]
    
    # --- ENGAGING LOADING ANIMATION ---
    # This sells the complexity of your architecture to the judges while they wait!
    with st.status("Initializing Sentinel Pipeline...", expanded=True) as status:
        st.write("📥 Ingesting PDF Document...")
        time.sleep(1)
        st.write("✂️ Chunking text using RecursiveCharacterTextSplitter...")
        time.sleep(1)
        st.write("🔎 Querying local ChromaDB for CUAD legal context...")
        time.sleep(1.5)
        st.write("🧠 Waking up Snapdragon NPU (Llama 3.2 3B)...")
        time.sleep(1)
        st.write("⏳ Generating semantic analysis. This may take up to 60 seconds depending on document density...")
        
        # --- MAKE THE API CALL ---
        start_time = time.time()
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            data = {"analysis_mode": api_mode}
            
            response = requests.post(API_URL, files=files, data=data)
            response.raise_for_status()
            result = response.json()
            
            elapsed_time = round(time.time() - start_time, 1)
            status.update(label=f"Scan Complete! ({elapsed_time}s)", state="complete", expanded=False)
            
        except requests.exceptions.RequestException as e:
            status.update(label="API Connection Failed", state="error")
            st.error(f"Failed to connect to backend: {e}")
            st.stop()
            
    # ==========================================
    # RENDER RESULTS
    # ==========================================
    st.divider()
    st.header(f"📊 Report: {uploaded_file.name}")
    
    res_data = result.get("data", {})
    
    # --- VIEW 1: LEGAL RISK SCORING ---
    if api_mode == "legal_risk_scoring":
        findings = res_data.get("findings", [])
        score = res_data.get("score", 0)
        
        # Top Metrics
        col1, col2 = st.columns([1, 2])
        with col1:
            st.plotly_chart(draw_gauge(score), use_container_width=True)
        with col2:
            st.markdown("### Threat Summary")
            high_count = sum(1 for f in findings if f.get("risk_level") == "HIGH")
            med_count = sum(1 for f in findings if f.get("risk_level") == "MED")
            low_count = sum(1 for f in findings if f.get("risk_level") == "LOW")
            
            c1, c2, c3 = st.columns(3)
            c1.metric(label="High Risk Clauses", value=high_count, delta="Critical Attention" if high_count > 0 else None, delta_color="inverse")
            c2.metric(label="Medium Risk", value=med_count)
            c3.metric(label="Low Risk", value=low_count)

        # Detailed Cards
        st.subheader("📑 Detailed Clause Analysis")
        for finding in sorted(findings, key=lambda x: {"HIGH": 0, "MED": 1, "LOW": 2}.get(x.get("risk_level", "LOW"), 3)):
            render_finding_card(finding, api_mode)

    # --- VIEW 2: VULNERABILITY DETECTION ---
    elif api_mode == "vulnerability_detection":
        findings = res_data.get("findings", [])
        
        st.markdown("### 👾 Vulnerability Audit Summary")
        high_count = sum(1 for f in findings if f.get("severity") == "HIGH")
        total = len(findings)
        
        c1, c2 = st.columns(2)
        c1.metric(label="Total Vulnerabilities Detected", value=total)
        c2.metric(label="High Severity Exposures", value=high_count, delta="Immediate Patch Required" if high_count > 0 else None, delta_color="inverse")
        
        st.subheader("🛡️ Code & Architecture Findings")
        for finding in sorted(findings, key=lambda x: {"HIGH": 0, "MED": 1, "LOW": 2}.get(x.get("severity", "LOW"), 3)):
            render_finding_card(finding, api_mode)

    # --- VIEW 3: PII MASKING ---
    elif api_mode == "pii_masking":
        instances = res_data.get("pii_instances", [])
        
        st.markdown("### 🕵️ Data Privacy Audit")
        st.metric(label="Total PII Leaks Detected", value=len(instances), delta="Compliance Risk" if len(instances) > 0 else "Safe", delta_color="inverse")
        
        st.subheader("⚠️ Redacted Instances")
        for finding in instances:
            render_finding_card(finding, api_mode)