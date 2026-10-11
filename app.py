import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import json
import io
from datetime import datetime

# -----------------------------------------------------------------------------
# PAGE CONFIG & CSS ANIMATIONS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Enterprise ISMS Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Light (Default) / Dark themes & animations
def inject_custom_css(theme):
    if theme == "Dark":
        bg_color = "#0e1117"
        card_bg = "#1e222d"
        text_color = "#ffffff"
        border_color = "#2e3440"
    else:  # Light Mode (Default)
        bg_color = "#f8f9fa"
        card_bg = "#ffffff"
        text_color = "#1f2937"
        border_color = "#e5e7eb"

    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .metric-card {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease-in-out;
            animation: fadeIn 0.6s ease-in-out;
        }}
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            margin-top: 5px;
        }}
        .metric-label {{
            font-size: 0.875rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .stButton>button {{
            border-radius: 8px;
            transition: all 0.2s ease;
        }}
        .stButton>button:hover {{
            transform: scale(1.02);
        }}
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "current_user" not in st.session_state:
    st.session_state.current_user = "admin@organization.internal"

inject_custom_css(st.session_state.theme)

# -----------------------------------------------------------------------------
# SUPABASE CONNECTION
# -----------------------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def log_action(user_email: str, action: str, entity: str, details: str):
    try:
        supabase.table("audit_logs").insert({
            "user_email": user_email,
            "action": action,
            "entity": entity,
            "details": details
        }).execute()
    except Exception as e:
        st.warning(f"Audit log error: {e}")

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🛡️ Enterprise ISMS")
    st.caption("In-House Compliance & Risk Portal")
    st.divider()

    menu = st.radio(
        "Navigation",
        ["📊 Executive Dashboard", "⚠️ Risk Register", "📋 Gap Assessment", "📜 Audit Logs", "⚙️ Settings & Backups"],
        index=0
    )

    st.divider()
    
    # Theme Switcher
    st.subheader("Appearance")
    selected_theme = st.selectbox("View Mode", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1)
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    st.caption("Connected to local Enterprise DB")

# -----------------------------------------------------------------------------
# 1. EXECUTIVE DASHBOARD
# -----------------------------------------------------------------------------
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Dashboard")
    st.caption("Real-time Overview of Organizational Cyber & Operational Risks")

    # Fetch Data
    risks_res = supabase.table("risks").select("*").execute()
    risks_df = pd.DataFrame(risks_res.data) if risks_res.data else pd.DataFrame()

    # KPI Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    
    total_risks = len(risks_df) if not risks_df.empty else 0
    critical_risks = len(risks_df[risks_df['severity'] == 'Critical']) if not risks_df.empty else 0
    open_risks = len(risks_df[risks_df['status'] == 'Open']) if not risks_df.empty else 0
    resolved_risks = len(risks_df[risks_df['status'] == 'Resolved']) if not risks_df.empty else 0

    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Identified Risks</div><div class="metric-value">{total_risks}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label" style="color:#ef4444;">Critical Severity</div><div class="metric-value" style="color:#ef4444;">{critical_risks}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label" style="color:#f59e0b;">Action Required (Open)</div><div class="metric-value" style="color:#f59e0b;">{open_risks}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label" style="color:#10b981;">Resolved / Mitigated</div><div class="metric-value" style="color:#10b981;">{resolved_risks}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    if not risks_df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Risks by Domain")
            fig_domain = px.bar(
                risks_df, x="domain", color="severity",
                barmode="group",
                color_discrete_map={"Critical": "#ef4444", "High": "#f97316", "Medium": "#eab308", "Low": "#3b82f6"}
            )
            fig_domain.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_domain, use_container_width=True)

        with c2:
            st.subheader("Risk Status Breakdown")
            fig_status = px.pie(risks_df, names="status", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_status.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_status, use_container_width=True)

        # Export Button
        csv = risks_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Dashboard Data (CSV)", data=csv, file_name="isms_dashboard_export.csv", mime="text/csv")
    else:
        st.info("No risk records found. Go to 'Risk Register' to log your first risk.")

# -----------------------------------------------------------------------------
# 2. RISK REGISTER & LIVE INDEX SUGGESTION
# -----------------------------------------------------------------------------
elif menu == "⚠️ Risk Register":
    st.title("⚠️ Risk Register & Live Indexing")

    tab1, tab2 = st.tabs(["📋 View All Risks", "➕ Log New Risk"])

    with tab1:
        risks_res = supabase.table("risks").select("*").execute()
        if risks_res.data:
            df = pd.DataFrame(risks_res.data)
            st.dataframe(df, use_container_width=True)
            
            # Export Sample CSV Template
            sample_df = pd.DataFrame([{
                "title": "Example Server Outage",
                "description": "Primary database server unresponsiveness",
                "domain": "IT Infrastructure",
                "severity": "High",
                "likelihood": 4,
                "impact": 4,
                "owner_email": "admin@org.internal"
            }])
            st.download_button("📥 Download CSV Template for Import", data=sample_df.to_csv(index=False), file_name="risk_import_template.csv")
        else:
            st.info("No risks currently registered.")

    with tab2:
        st.subheader("Log a New Risk with Real-Time Smart Suggestion")

        # Live Suggestion Box
        title_input = st.text_input("Risk Title / Summary", key="risk_title_input", placeholder="Start typing e.g. outage, phishing, backup...")
        
        if title_input:
            # Query risk_library for real-time indexing suggestion
            lib_res = supabase.table("risk_library").select("*").ilike("keyword", f"%{title_input}%").execute()
            if lib_res.data:
                st.markdown("💡 **Live Indexed Risk Suggestions Found:**")
                for item in lib_res.data:
                    st.warning(f"• **{item['suggested_title']}** | Domain: *{item['domain']}* | Recommended Control: `{item['recommended_control']}`")

        with st.form("new_risk_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                domain = st.selectbox("Domain", ["IT Infrastructure", "Data Privacy", "Cybersecurity", "Business Continuity", "Physical Security"])
                severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
                likelihood = st.slider("Likelihood (1-5)", 1, 5, 3)
            with col_b:
                impact = st.slider("Impact (1-5)", 1, 5, 3)
                owner_email = st.text_input("Risk Owner Email", value=st.session_state.current_user)
                description = st.text_area("Detailed Description")

            submitted = st.form_submit_button("Submit & Log Risk")
            if submitted and title_input:
                supabase.table("risks").insert({
                    "title": title_input,
                    "description": description,
                    "domain": domain,
                    "severity": severity,
                    "likelihood": likelihood,
                    "impact": impact,
                    "owner_email": owner_email,
                    "status": "Open"
                }).execute()

                log_action(st.session_state.current_user, "CREATE_RISK", "Risks", f"Created risk: {title_input}")
                st.success("Risk logged successfully!")
                st.rerun()

# -----------------------------------------------------------------------------
# 3. GAP ASSESSMENT & READINESS SCORE
# -----------------------------------------------------------------------------
elif menu == "📋 Gap Assessment":
    st.title("📋 ISO 27001 Gap Assessment")
    st.caption("Evaluate readiness score for internal/external audits")

    clauses = [
        {"code": "A.5", "name": "Information Security Policies", "weight": 20},
        {"code": "A.6", "name": "Organization of Information Security", "weight": 20},
        {"code": "A.9", "name": "Access Control", "weight": 30},
        {"code": "A.12", "name": "Operations Security", "weight": 30}
    ]

    scores = []
    for c in clauses:
        val = st.slider(f"{c['code']} - {c['name']} Compliance (%)", 0, 100, 75, key=c['code'])
        scores.append(val)

    readiness_score = sum(scores) / len(scores)
    
    st.divider()
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        st.metric("Overall ISO 27001 Readiness Score", f"{readiness_score:.1f}%")
        if readiness_score >= 80:
            st.success("Status: Ready for Formal Audit")
        else:
            st.warning("Status: Gap Mitigation Required")

    with col_s2:
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=scores,
            theta=[c['code'] for c in clauses],
            fill='toself'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
        st.plotly_chart(fig_radar, use_container_width=True)

# -----------------------------------------------------------------------------
# 4. AUDIT LOGS
# -----------------------------------------------------------------------------
elif menu == "📜 Audit Logs":
    st.title("📜 Audit Trail & System Activity")
    st.caption("Immutable system events logged across all operations")

    logs_res = supabase.table("audit_logs").select("*").order("created_at", desc=True).execute()
    if logs_res.data:
        logs_df = pd.DataFrame(logs_res.data)
        st.dataframe(logs_df, use_container_width=True)
    else:
        st.info("No log records captured yet.")

# -----------------------------------------------------------------------------
# 5. SETTINGS & LOCAL BACKUP
# -----------------------------------------------------------------------------
elif menu == "⚙️ Settings & Backups":
    st.title("⚙️ System Backup & In-House Configuration")

    st.subheader("💾 Data Backup & Disaster Recovery")
    st.write("Generate a full local JSON/CSV dump of the database to ensure business continuity.")

    if st.button("Generate Immediate Local Backup"):
        r = supabase.table("risks").select("*").execute()
        a = supabase.table("audit_logs").select("*").execute()
        
        backup_data = {
            "timestamp": str(datetime.now()),
            "risks": r.data,
            "audit_logs": a.data
        }
        
        json_str = json.dumps(backup_data, indent=2)
        st.download_button(
            label="💾 Download Backup File (.json)",
            data=json_str,
            file_name=f"isms_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        log_action(st.session_state.current_user, "MANUAL_BACKUP", "System", "Executed manual database backup")