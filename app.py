import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import json
from datetime import datetime, timedelta
import random

# -----------------------------------------------------------------------------
# PAGE CONFIG & CSS ANIMATIONS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Enterprise ISMS Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded" # Restored sidebar to be open by default
)

# Custom CSS for Themes, Animations, & Sidebar Block Menu
def inject_custom_css(theme):
    if theme == "Dark":
        bg_color = "#0e1117"
        card_bg = "#1e222d"
        text_color = "#ffffff"
        border_color = "#2e3440"
        hover_bg = "#262b38"
        accent_color = "#3b82f6"
    else:  
        bg_color = "#f8f9fa"
        card_bg = "#ffffff"
        text_color = "#1f2937"
        border_color = "#e5e7eb"
        hover_bg = "#f3f4f6"
        accent_color = "#3b82f6"

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
        .metric-value {{ font-size: 2rem; font-weight: 700; margin-top: 5px; }}
        .metric-label {{ font-size: 0.875rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* --- SIDEBAR BLOCK MENU CSS --- */
        /* 1. Hide the radio button circles completely */
        [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {{
            display: none !important;
        }}
        
        /* 2. Style the radio labels as block items */
        [data-testid="stSidebar"] div[role="radiogroup"] > label {{
            background-color: {card_bg};
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid {border_color};
            margin-bottom: 10px;
            transition: all 0.2s ease-in-out;
            width: 100%;
            cursor: pointer;
        }}
        
        /* 3. Hover Effect: Change background, border, and zoom */
        [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
            background-color: {hover_bg};
            transform: scale(1.03);
            border-color: {accent_color};
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
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
# SUPABASE CONNECTION & SAMPLE DATA GENERATOR
# -----------------------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def get_risk_data():
    res = supabase.table("risks").select("*").execute()
    if res.data:
        return pd.DataFrame(res.data), False
    else:
        # Generate Professional Sample Data for Presentation
        domains = ["IT Infrastructure", "Data Privacy", "Cybersecurity", "Business Continuity", "Physical Security"]
        statuses = ["Open", "In-Progress", "Resolved", "Monitoring"]
        severities = ["Low", "Medium", "High", "Critical"]
        
        sample_data = []
        for i in range(1, 26):
            l, i_score = random.randint(1, 5), random.randint(1, 5)
            sev = severities[min(3, (l * i_score) // 6)]
            sample_data.append({
                "id": f"dummy-{i}",
                "title": f"Sample Risk Profile {i}: {random.choice(['Outage', 'Leak', 'Compliance', 'Access Control'])}",
                "domain": random.choice(domains),
                "status": random.choice(statuses),
                "severity": sev,
                "likelihood": l,
                "impact": i_score,
                "risk_score": l * i_score,
                "owner_email": "demo@organization.internal",
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
            })
        return pd.DataFrame(sample_data), True

risks_df, is_sample_data = get_risk_data()

# -----------------------------------------------------------------------------
# SIDEBAR & TOP-RIGHT THEME TOGGLE
# -----------------------------------------------------------------------------
# Top right theme toggle
col_title, col_theme = st.columns([9, 1])
with col_theme:
    theme_icon = "🌙" if st.session_state.theme == "Light" else "☀️"
    if st.button(theme_icon, help="Toggle Dark/Light Mode"):
        st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
        st.rerun()

# Sidebar Navigation Block Menu
with st.sidebar:
    st.markdown("### 🛡️ ISMS Portal")
    st.caption("In-House Compliance & Risk")
    st.write("") # Spacer
    
    menu = st.radio(
        "Navigation",
        ["📊 Executive Dashboard", "⚠️ Risk Register", "📋 Gap Assessment", "📜 Audit Logs", "⚙️ Settings"],
        label_visibility="collapsed" # Hides the word "Navigation"
    )

# -----------------------------------------------------------------------------
# 1. EXECUTIVE DASHBOARD
# -----------------------------------------------------------------------------
if menu == "📊 Executive Dashboard":
    with col_title:
        st.title("Executive Dashboard")
    st.markdown("#### Real-time Organizational Risk Overview")
    
    if is_sample_data:
        st.info("💡 **Presentation Mode:** Displaying sample data because the database is empty.")

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    total_risks = len(risks_df)
    critical_risks = len(risks_df[risks_df['severity'] == 'Critical'])
    open_risks = len(risks_df[risks_df['status'] == 'Open'])
    resolved_risks = len(risks_df[risks_df['status'] == 'Resolved'])

    with col1: st.markdown(f'<div class="metric-card"><div class="metric-label">Total Identified Risks</div><div class="metric-value">{total_risks}</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><div class="metric-label" style="color:#ef4444;">Critical Severity</div><div class="metric-value" style="color:#ef4444;">{critical_risks}</div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card"><div class="metric-label" style="color:#f59e0b;">Action Required (Open)</div><div class="metric-value" style="color:#f59e0b;">{open_risks}</div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="metric-card"><div class="metric-label" style="color:#10b981;">Resolved / Mitigated</div><div class="metric-value" style="color:#10b981;">{resolved_risks}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Dashboard Customization / Filters
    with st.expander("🛠️ Customize Dashboard View"):
        selected_domains = st.multiselect("Filter by Domain", options=risks_df['domain'].unique(), default=risks_df['domain'].unique())
    
    filtered_df = risks_df[risks_df['domain'].isin(selected_domains)]

    # Multi-Charts
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    
    with c1:
        st.subheader("Risks by Domain (Bar)")
        fig_domain = px.bar(
            filtered_df, x="domain", color="severity",
            barmode="group",
            color_discrete_map={"Critical": "#ef4444", "High": "#f97316", "Medium": "#eab308", "Low": "#3b82f6"}
        )
        fig_domain.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_domain, use_container_width=True)

    with c2:
        st.subheader("Status (Donut)")
        fig_status = px.pie(filtered_df, names="status", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_status.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_status, use_container_width=True)

    with c3:
        st.subheader("Risk Matrix (Point / Scatter)")
        # Point chart for Impact vs Likelihood
        fig_matrix = px.scatter(
            filtered_df, x="impact", y="likelihood", 
            color="severity", size="risk_score", hover_data=["title"],
            color_discrete_map={"Critical": "#ef4444", "High": "#f97316", "Medium": "#eab308", "Low": "#3b82f6"}
        )
        fig_matrix.update_layout(
            xaxis=dict(range=[0.5, 5.5], title="Impact"),
            yaxis=dict(range=[0.5, 5.5], title="Likelihood"),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_matrix, use_container_width=True)

# -----------------------------------------------------------------------------
# 2. RISK REGISTER
# -----------------------------------------------------------------------------
elif menu == "⚠️ Risk Register":
    with col_title: st.title("⚠️ Risk Register")
    st.markdown("#### Live Indexing & Records")
    st.dataframe(risks_df, use_container_width=True)
    
    st.divider()
    st.subheader("Log a New Risk")
    with st.form("new_risk_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            title = st.text_input("Risk Title")
            domain = st.selectbox("Domain", ["IT Infrastructure", "Data Privacy", "Cybersecurity"])
            severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
        with col_b:
            likelihood = st.slider("Likelihood (1-5)", 1, 5, 3)
            impact = st.slider("Impact (1-5)", 1, 5, 3)
            
        if st.form_submit_button("Submit & Log Risk") and title:
            supabase.table("risks").insert({
                "title": title, "domain": domain, "severity": severity,
                "likelihood": likelihood, "impact": impact, "status": "Open",
                "owner_email": st.session_state.current_user
            }).execute()
            st.success("Risk logged to database!")
            st.rerun()

# -----------------------------------------------------------------------------
# 3. GAP ASSESSMENT
# -----------------------------------------------------------------------------
elif menu == "📋 Gap Assessment":
    with col_title: st.title("📋 Gap Assessment")
    st.markdown("#### ISO 27001 Readiness Checklist")
    st.info("Pre-audit checklist module goes here.")

# -----------------------------------------------------------------------------
# 4. AUDIT LOGS
# -----------------------------------------------------------------------------
elif menu == "📜 Audit Logs":
    with col_title: st.title("📜 Audit Logs")
    st.markdown("#### Audit Trail & System Activity")
    logs_res = supabase.table("audit_logs").select("*").order("created_at", desc=True).execute()
    if logs_res.data:
        st.dataframe(pd.DataFrame(logs_res.data), use_container_width=True)
    else:
        st.info("No log records captured yet.")

# -----------------------------------------------------------------------------
# 5. SETTINGS
# -----------------------------------------------------------------------------
elif menu == "⚙️ Settings":
    with col_title: st.title("⚙️ Settings")
    st.markdown("#### System Backup & Settings")
    if st.button("Generate Immediate Local Backup"):
        st.success("Backup downloaded (Placeholder for demo)")
