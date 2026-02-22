import streamlit as st
import requests

API_BASE = "http://localhost:8000"

SELECTION_OPTIONS = {
    "Legal Risk Scoring": "legal_risk_scoring",
    "PII Masking": "pii_masking",
    "Vulnerability Detection": "vulnerability_detection",
}

SEV_COLOR = {"HIGH": "red", "MEDIUM": "orange", "LOW": "green"}
SEV_ICON = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}

st.set_page_config(page_title="Sentinel-Edge", layout="wide", page_icon="🛡️")

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── Layout ────────────────────────────────────────────────────────────────────
st.title("🛡️ Sentinel-Edge")
st.caption("Air-gapped AI security auditor — 100% offline")

col_sidebar, col_main = st.columns([1, 2], gap="large")

# ── LEFT: controls + chat ─────────────────────────────────────────────────────
with col_sidebar:
    st.subheader("Settings")

    selection_label = st.selectbox(
        "Analysis type",
        options=list(SELECTION_OPTIONS.keys()),
    )
    selection = SELECTION_OPTIONS[selection_label]

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    st.subheader("Chat")
    user_input = st.text_area("Question or additional instructions", height=100, key="chat_input")
    send = st.button("Analyze", use_container_width=True, type="primary")

    st.divider()
    st.caption("Conversation history")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── RIGHT: dashboard ──────────────────────────────────────────────────────────
with col_main:
    st.subheader("Results Dashboard")

    if st.session_state.last_result is None:
        st.info("Upload a PDF and click **Analyze** to see results here.")
    else:
        result = st.session_state.last_result
        mode = result["selection"]
        findings = result.get("findings", [])
        pii_instances = result.get("pii_instances", [])

        # ── Header metrics ────────────────────────────────────────────────
        high = sum(1 for f in findings if f.get("severity", "").upper() == "HIGH")
        med  = sum(1 for f in findings if f.get("severity", "").upper() == "MEDIUM")
        low  = sum(1 for f in findings if f.get("severity", "").upper() == "LOW")

        if mode == "legal_risk_scoring":
            score = result.get("score", 0)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Risk Score", f"{score}/10")
            m2.metric("HIGH", high, delta_color="inverse")
            m3.metric("MEDIUM", med, delta_color="inverse")
            m4.metric("LOW", low, delta_color="off")

        elif mode == "pii_masking":
            st.metric("PII Instances", len(pii_instances))

        elif mode == "vulnerability_detection":
            m1, m2, m3 = st.columns(3)
            m1.metric("HIGH", high)
            m2.metric("MEDIUM", med)
            m3.metric("LOW", low)

        st.divider()

        # ── Findings table ────────────────────────────────────────────────
        if mode == "pii_masking":
            if pii_instances:
                st.subheader(f"PII Instances ({len(pii_instances)})")
                for item in pii_instances:
                    with st.expander(f"`{item.get('type', 'PII')}` — {str(item.get('value', item))[:80]}"):
                        st.json(item)
            else:
                st.success("No PII detected.")

        else:
            if findings:
                st.subheader(f"Findings ({len(findings)})")
                for i, f in enumerate(findings):
                    sev = f.get("severity", "UNKNOWN").upper()
                    icon = SEV_ICON.get(sev, "⚪")
                    title = f.get("type") or f.get("title") or f"Finding {i+1}"
                    desc = f.get("description", "")
                    rec = f.get("recommendation", "")

                    with st.expander(f"{icon} [{sev}] {title}"):
                        if desc:
                            st.markdown(f"**Description:** {desc}")
                        if rec:
                            st.markdown(f"**Recommendation:** {rec}")
                        # show any extra keys
                        extra = {k: v for k, v in f.items() if k not in {"severity", "type", "title", "description", "recommendation"}}
                        if extra:
                            st.json(extra)
            else:
                st.success("No findings.")

        with st.expander("Raw JSON response"):
            st.json(result)

# ── Handle analyze ────────────────────────────────────────────────────────────
if send:
    if not uploaded_file:
        with col_sidebar:
            st.error("Please upload a PDF first.")
    else:
        prompt = user_input.strip()
        display_prompt = prompt if prompt else f"Run **{selection_label}** on `{uploaded_file.name}`"
        st.session_state.messages.append({"role": "user", "content": display_prompt})

        with st.spinner("Analyzing…"):
            try:
                response = requests.post(
                    f"{API_BASE}/api/analyze",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                    data={"selection": selection, "prompt": prompt},
                    timeout=300,
                )
                response.raise_for_status()
                result = response.json()
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend at http://localhost:8000 — is it running?")
                st.stop()
            except requests.exceptions.HTTPError as e:
                st.error(f"Backend error: {e.response.text}")
                st.stop()

        st.session_state.last_result = result

        # Summarize in chat
        findings = result.get("findings", [])
        pii = result.get("pii_instances", [])
        score = result.get("score")

        if result["selection"] == "legal_risk_scoring":
            summary = f"Analysis complete. Risk score **{score}/10** with {len(findings)} finding(s)."
        elif result["selection"] == "pii_masking":
            summary = f"Analysis complete. Found **{len(pii)}** PII instance(s)."
        else:
            summary = f"Analysis complete. Found **{len(findings)}** vulnerability/vulnerabilities."

        st.session_state.messages.append({"role": "assistant", "content": summary})
        st.rerun()
