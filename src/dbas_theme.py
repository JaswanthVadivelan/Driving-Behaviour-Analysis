# src/dbas_theme.py
# Professional white/light conference theme for DBAS.

import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu

# ── Navigation constants ──────────────────────────────────────────────────────────
NAV_OPTIONS  = ["Dashboard", "Live Scoring", "Fleet Map", "Driver Leaderboard", "Risk Heatmap", "Vehicle Profile", "Alerts", "Reports", "Model Performance"]
NAV_ICONS    = ["grid", "speedometer2", "map", "trophy", "fire", "person-badge", "exclamation-triangle", "file-earmark-bar-graph", "cpu"]
NAV_PAGE_MAP = {
    "Dashboard":          "app.py",
    "Live Scoring":       "pages/1_Live_Scoring.py",
    "Fleet Map":          "pages/7_Fleet_Map.py",
    "Driver Leaderboard": "pages/8_Driver_Leaderboard.py",
    "Risk Heatmap":       "pages/9_Risk_Heatmap.py",
    "Vehicle Profile":    "pages/6_Vehicle_Profile.py",
    "Alerts":             "pages/4_Alerts.py",
    "Reports":            "pages/5_Reports.py",
    "Model Performance":  "pages/11_Model_Performance.py",
}

# ── Shared Plotly layout ──────────────────────────────────────────────────────────
PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'DM Sans', sans-serif", color="#64748b", size=11),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e2e8f0",
        borderwidth=1,
        font=dict(size=11),
    ),
)

AXIS = dict(
    gridcolor="rgba(100,116,139,0.1)",
    zerolinecolor="rgba(100,116,139,0.15)",
    tickfont=dict(family="'DM Sans', sans-serif", size=11, color="#94a3b8"),
    linecolor="#e2e8f0",
)

def get_plotly_layout():
    theme = st.session_state.get('theme', 'Light')
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'DM Sans', sans-serif", color="#64748b" if theme=="Light" else "#9ca3af", size=11),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)" if theme=="Light" else "rgba(17,24,39,0.9)",
            bordercolor="#e2e8f0" if theme=="Light" else "#1f2937",
            borderwidth=1,
            font=dict(size=11),
        ),
    )

def get_axis_layout():
    theme = st.session_state.get('theme', 'Light')
    return dict(
        gridcolor="rgba(100,116,139,0.1)" if theme=="Light" else "rgba(255,255,255,0.05)",
        zerolinecolor="rgba(100,116,139,0.15)" if theme=="Light" else "rgba(255,255,255,0.1)",
        tickfont=dict(family="'DM Sans', sans-serif", size=11, color="#94a3b8" if theme=="Light" else "#9ca3af"),
        linecolor="#e2e8f0" if theme=="Light" else "#1f2937",
    )

# ── Global CSS ────────────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  /* Backgrounds */
  --bg:          #f8fafc;
  --surface:     #ffffff;
  --surface2:    #f1f5f9;
  --surface3:    #e8f0fe;

  /* Borders */
  --border:      #e2e8f0;
  --border-med:  #cbd5e1;

  /* Text */
  --text:        #0f172a;
  --text-2:      #334155;
  --muted:       #64748b;
  --dim:         #94a3b8;

  /* Brand */
  --blue:        #1a56db;
  --blue-light:  #eff6ff;
  --blue-mid:    #dbeafe;

  /* Semantic */
  --green:       #059669;
  --green-light: #ecfdf5;
  --amber:       #d97706;
  --amber-light: #fffbeb;
  --red:         #dc2626;
  --red-light:   #fef2f2;
  --purple:      #7c3aed;
  --purple-light:#f5f3ff;

  /* Typography */
  --font-d:  'Plus Jakarta Sans', sans-serif;
  --font-b:  'DM Sans', sans-serif;
  --font-m:  'JetBrains Mono', monospace;

  /* Shape */
  --radius:    6px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  /* Shadow */
  --shadow-sm: 0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04);
  --shadow:    0 4px 12px rgba(15,23,42,0.08), 0 2px 4px rgba(15,23,42,0.04);
  --shadow-lg: 0 10px 30px rgba(15,23,42,0.1), 0 4px 8px rgba(15,23,42,0.06);
}

/* ── Base ── */
html, body, [class*="css"] {
  font-family: var(--font-b) !important;
  color: var(--text) !important;
}

.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background-color: var(--bg) !important;
}

section[data-testid="stSidebar"]  { display: none !important; }
div[data-testid="stSidebarNav"]   { display: none !important; }
#MainMenu, footer, header         { visibility: hidden !important; }
.block-container {
  padding: 0 2.5rem 3rem !important;
  max-width: 100% !important;
}

/* ── Topbar ── */
.dbas-topbar {
  position: sticky; top: 0; z-index: 999;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 2.5rem;
  height: 60px;
  background: rgba(255,255,255,0.95);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(12px);
  margin: 0 -2.5rem;
  box-shadow: var(--shadow-sm);
}
.dbas-brand { display: flex; align-items: center; gap: 12px; }
.dbas-logo {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, #1a56db, #3b82f6);
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px rgba(26,86,219,0.3);
}
.dbas-logo svg { width: 18px; height: 18px; }
.dbas-brand-name {
  font-family: var(--font-d); font-size: 16px; font-weight: 800;
  letter-spacing: -0.01em; color: var(--text); line-height: 1.1;
}
.dbas-brand-sub {
  font-family: var(--font-m); font-size: 9px; color: var(--muted);
  letter-spacing: 0.06em; text-transform: uppercase;
}
.dbas-live {
  display: flex; align-items: center; gap: 7px;
  font-family: var(--font-m); font-size: 10px;
  letter-spacing: 0.08em; color: var(--green); text-transform: uppercase;
  background: var(--green-light);
  padding: 5px 12px; border-radius: 20px;
  border: 1px solid rgba(5,150,105,0.2);
}
.dbas-live-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green); box-shadow: 0 0 6px rgba(5,150,105,0.5);
  animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{ opacity:1; } 50%{ opacity:0.3; } }
.dbas-time {
  font-family: var(--font-m); font-size: 11px;
  color: var(--muted); letter-spacing: 0.04em;
  background: var(--surface2); padding: 5px 12px;
  border-radius: 6px; border: 1px solid var(--border);
}

/* ── Page header ── */
.dbas-page-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  padding: 28px 0 22px;
  border-bottom: 2px solid var(--border);
  margin-bottom: 28px;
}
.dbas-page-title {
  font-family: var(--font-d); font-size: 26px; font-weight: 800;
  letter-spacing: -0.02em; color: var(--text);
}
.dbas-page-sub {
  font-size: 13px; color: var(--muted);
  font-weight: 400; margin-top: 5px;
}
.dbas-badge {
  font-family: var(--font-m); font-size: 9px;
  letter-spacing: 0.1em; text-transform: uppercase;
  padding: 5px 14px; border-radius: 20px;
  background: var(--blue-light);
  border: 1px solid var(--blue-mid);
  color: var(--blue); font-weight: 500;
}

/* ── Section label ── */
.dbas-section {
  display: flex; align-items: center; gap: 10px;
  font-family: var(--font-m); font-size: 9px;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--muted); margin: 28px 0 16px;
  font-weight: 500;
}
.dbas-section::after {
  content: ''; flex: 1; height: 1px; background: var(--border);
}

/* ── KPI cards ── */
.kpi {
  background: var(--surface);
  border-radius: var(--radius-xl);
  padding: 22px 24px;
  position: relative; overflow: hidden;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s, transform 0.2s, border-color 0.2s;
  cursor: default;
  animation: fadeUp 0.4s ease both;
}
.kpi:hover {
  box-shadow: var(--shadow);
  transform: translateY(-2px);
  border-color: var(--border-med);
}
.kpi::before {
  content: ''; position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}
.kpi.blue::before  { background: linear-gradient(90deg, #1a56db, #3b82f6); }
.kpi.green::before { background: linear-gradient(90deg, #059669, #10b981); }
.kpi.amber::before { background: linear-gradient(90deg, #d97706, #f59e0b); }
.kpi.red::before   { background: linear-gradient(90deg, #dc2626, #ef4444); }

.kpi-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 14px; font-size: 18px;
}
.blue  .kpi-icon { background: var(--blue-light);   }
.green .kpi-icon { background: var(--green-light);  }
.amber .kpi-icon { background: var(--amber-light);  }
.red   .kpi-icon { background: var(--red-light);    }

.kpi-label {
  font-family: var(--font-m); font-size: 9px;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 8px; font-weight: 500;
}
.kpi-val {
  font-family: var(--font-d); font-size: 34px; font-weight: 800;
  line-height: 1; letter-spacing: -0.02em;
}
.blue  .kpi-val { color: var(--blue);  }
.green .kpi-val { color: var(--green); }
.amber .kpi-val { color: var(--amber); }
.red   .kpi-val { color: var(--red);   }

.kpi-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 12px; padding-top: 12px;
  border-top: 1px solid var(--border);
}
.kpi-sub  { font-size: 11.5px; color: var(--muted); font-weight: 400; }
.kpi-delta {
  font-family: var(--font-m); font-size: 9.5px;
  padding: 3px 9px; border-radius: 20px; font-weight: 600;
}
.d-up  { background: var(--green-light); color: var(--green); border: 1px solid rgba(5,150,105,0.2); }
.d-dn  { background: var(--red-light);   color: var(--red);   border: 1px solid rgba(220,38,38,0.2); }
.d-neu { background: var(--amber-light); color: var(--amber); border: 1px solid rgba(217,119,6,0.2); }

/* ── Content cards ── */
.content-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 20px 24px;
  margin-bottom: 14px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s, border-color 0.2s;
  animation: fadeUp 0.4s ease both;
}
.content-card:hover {
  box-shadow: var(--shadow);
  border-color: var(--border-med);
}
.content-card-title {
  font-family: var(--font-d); font-size: 14px; font-weight: 700;
  letter-spacing: -0.01em; color: var(--text); margin-bottom: 4px;
}
.content-card-tag {
  font-family: var(--font-m); font-size: 9px; color: var(--muted);
  letter-spacing: 0.1em; text-transform: uppercase;
  display: inline-block; padding: 3px 9px;
  border: 1px solid var(--border); border-radius: 20px;
  margin-bottom: 8px; background: var(--surface2);
}

/* ── Form inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
  background: var(--surface) !important;
  border: 1px solid var(--border-med) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--font-b) !important;
  font-size: 13.5px !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px rgba(26,86,219,0.1) !important;
}
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stFileUploader"] label,
[data-testid="stCheckbox"] label {
  font-family: var(--font-m) !important;
  font-size: 10px !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
  font-weight: 500 !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
  background: var(--surface) !important;
  border: 1px solid var(--border-med) !important;
  color: var(--text-2) !important;
  border-radius: var(--radius) !important;
  font-family: var(--font-b) !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  padding: 9px 20px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.15s ease !important;
}
[data-testid="stButton"] > button:hover {
  border-color: var(--blue) !important;
  color: var(--blue) !important;
  background: var(--blue-light) !important;
  box-shadow: var(--shadow) !important;
}
[data-testid="stButton"] > button[kind="primary"] {
  background: var(--blue) !important;
  border-color: var(--blue) !important;
  color: #fff !important;
  font-weight: 600 !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
  background: #1648c0 !important;
  border-color: #1648c0 !important;
  box-shadow: 0 4px 14px rgba(26,86,219,0.35) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
  background: var(--green-light) !important;
  border: 1px solid rgba(5,150,105,0.3) !important;
  color: var(--green) !important;
  border-radius: var(--radius) !important;
  font-family: var(--font-m) !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  letter-spacing: 0.04em !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: #d1fae5 !important;
  box-shadow: 0 2px 8px rgba(5,150,105,0.2) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] > section {
  background: var(--blue-light) !important;
  border: 2px dashed rgba(26,86,219,0.3) !important;
  border-radius: var(--radius-lg) !important;
}
[data-testid="stFileUploader"] > section:hover {
  border-color: var(--blue) !important;
  background: var(--blue-mid) !important;
}

/* ── st.metric ── */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 18px 22px !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stMetricLabel"] p {
  font-family: var(--font-m) !important;
  font-size: 9.5px !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--font-d) !important;
  font-size: 30px !important;
  font-weight: 800 !important;
  color: var(--text) !important;
}

/* ── Alerts/info boxes ── */
[data-testid="stInfo"] {
  background: var(--blue-light) !important;
  border: 1px solid var(--blue-mid) !important;
  border-radius: var(--radius) !important;
  color: var(--blue) !important;
  font-family: var(--font-b) !important;
  font-size: 13px !important;
}
[data-testid="stWarning"] {
  background: var(--amber-light) !important;
  border: 1px solid rgba(217,119,6,0.2) !important;
  border-radius: var(--radius) !important;
  color: var(--amber) !important;
  font-family: var(--font-b) !important;
}
[data-testid="stError"] {
  background: var(--red-light) !important;
  border: 1px solid rgba(220,38,38,0.2) !important;
  border-radius: var(--radius) !important;
  color: var(--red) !important;
  font-family: var(--font-b) !important;
}
[data-testid="stSuccess"] {
  background: var(--green-light) !important;
  border: 1px solid rgba(5,150,105,0.2) !important;
  border-radius: var(--radius) !important;
  color: var(--green) !important;
  font-family: var(--font-b) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ── Alert cards ── */
.dbas-alert-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  margin-bottom: 10px;
  display: flex; gap: 14px; align-items: flex-start;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s;
  animation: fadeUp 0.35s ease both;
}
.dbas-alert-card:hover { box-shadow: var(--shadow); }
.dbas-alert-card.critical {
  border-left: 3px solid var(--red);
  background: var(--red-light);
}
.dbas-alert-card.warning {
  border-left: 3px solid var(--amber);
  background: var(--amber-light);
}
.dbas-alert-icon {
  width: 36px; height: 36px; flex-shrink: 0;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}
.dbas-alert-icon.critical { background: rgba(220,38,38,0.12); }
.dbas-alert-icon.warning  { background: rgba(217,119,6,0.12);  }
.dbas-alert-body-title {
  font-family: var(--font-d); font-size: 13.5px; font-weight: 700;
  color: var(--text); margin-bottom: 5px;
}
.dbas-alert-meta {
  font-family: var(--font-b); font-size: 12px; color: var(--muted);
  margin-top: 3px;
}
.dbas-alert-meta span { color: var(--text-2); font-weight: 500; }

/* ── Stat chips ── */
.stat-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }
.stat-chip {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 10px 18px;
  font-family: var(--font-m); font-size: 10px; color: var(--muted);
  letter-spacing: 0.06em; box-shadow: var(--shadow-sm);
}
.stat-chip span {
  font-family: var(--font-d); font-size: 16px; font-weight: 700;
  color: var(--text); display: block; margin-top: 3px;
}

/* ── Typography ── */
h1, h2, h3 {
  font-family: var(--font-d) !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  letter-spacing: -0.01em !important;
}
p { font-family: var(--font-b) !important; color: var(--text-2) !important; }

/* ── Plotly ── */
.js-plotly-plot .plotly,
.js-plotly-plot .plotly .main-svg { background: transparent !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--surface2); }
::-webkit-scrollbar-thumb { background: var(--border-med); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* ── Animations ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
"""

NAV_STYLES = {
    "container": {
        "padding": "8px 0",
        "background-color": "#ffffff",
        "border-bottom": "1px solid #e2e8f0",
        "box-shadow": "0 1px 3px rgba(15,23,42,0.05)",
    },
    "icon": {"font-size": "13px", "color": "#64748b"},
    "nav-link": {
        "font-size": "13px",
        "font-family": "'DM Sans', sans-serif",
        "font-weight": "500",
        "padding": "7px 16px",
        "border-radius": "8px",
        "color": "#64748b",
        "margin": "0 3px",
    },
    "nav-link-selected": {
        "background-color": "#1a56db",
        "color": "#ffffff",
        "font-weight": "600",
        "box-shadow": "0 2px 8px rgba(26,86,219,0.3)",
    },
}


DARK_MODE_OVERRIDES = """
<style>
:root {
  --bg:          #0f172a;
  --surface:     #111827;
  --surface2:    #1f2937;
  --surface3:    #374151;
  --border:      #1f2937;
  --border-med:  #374151;
  --text:        #f9fafb;
  --text-2:      #e5e7eb;
  --muted:       #9ca3af;
  --dim:         #6b7280;
  --shadow-sm:   0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.3);
  --shadow:      0 4px 12px rgba(0,0,0,0.6), 0 2px 4px rgba(0,0,0,0.4);
  --shadow-lg:   0 10px 30px rgba(0,0,0,0.8), 0 4px 8px rgba(0,0,0,0.6);
}
.dbas-topbar {
  background: rgba(17,24,39,0.95) !important;
}
.stApp {
  color: #f9fafb !important;
  background-color: #0f172a !important;
}
</style>
"""

def apply_theme():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    if st.session_state.get('theme', 'Light') == 'Dark':
        st.markdown(DARK_MODE_OVERRIDES, unsafe_allow_html=True)


def render_topbar():
    now_str = datetime.now().strftime("%H:%M:%S  ·  %d %b %Y")
    st.markdown(f"""
    <div class="dbas-topbar">
      <div class="dbas-brand">
        <div class="dbas-logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div>
          <div class="dbas-brand-name">DBAS</div>
          <div class="dbas-brand-sub">Driving Behaviour Analysis</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:12px;">
        <div class="dbas-live">
          <div class="dbas-live-dot"></div>Live Monitoring
        </div>
        <div class="dbas-time">{now_str}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_nav(current_page: str):
    selected = option_menu(
        menu_title=None,
        options=NAV_OPTIONS,
        icons=NAV_ICONS,
        orientation="horizontal",
        default_index=NAV_OPTIONS.index(current_page),
        styles=NAV_STYLES,
    )
    if selected != current_page:
        st.switch_page(NAV_PAGE_MAP[selected])
    return selected


def render_page_header(title: str, subtitle: str, badge: str = ""):
    badge_html = f'<span class="dbas-badge">{badge}</span>' if badge else ""
    c1, c2 = st.columns([0.9, 0.1])
    with c1:
        st.markdown(f"""
        <div class="dbas-page-header" style="border-bottom:none; margin-bottom:5px;">
          <div>
            <div class="dbas-page-title">{title}</div>
            <div class="dbas-page-sub">{subtitle}</div>
          </div>
          {badge_html}
        </div>
        """, unsafe_allow_html=True)
    with c2:
        theme = st.session_state.get('theme', 'Light')
        btn_label = "☀️ Mode" if theme == "Dark" else "🌙 Mode"
        if st.button(btn_label, key=f"theme_toggle_{title}"):
            st.session_state.theme = "Light" if theme == "Dark" else "Dark"
            st.rerun()
    st.markdown("<hr style='margin-top:0; margin-bottom: 28px;' />", unsafe_allow_html=True)


def section(label: str):
    st.markdown(f'<div class="dbas-section">{label}</div>', unsafe_allow_html=True)


def kpi_card(label, value, sub, delta, delta_cls, color, icon="", delay=0):
    st.markdown(f"""
    <div class="kpi {color}" style="animation-delay:{delay}s">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-val">{value}</div>
      <div class="kpi-footer">
        <span class="kpi-sub">{sub}</span>
        <span class="kpi-delta {delta_cls}">{delta}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def stat_chips(stats: list):
    chips = "".join(
        f'<div class="stat-chip">{lbl}<span>{val}</span></div>'
        for lbl, val in stats
    )
    st.markdown(f'<div class="stat-row">{chips}</div>', unsafe_allow_html=True)


def page_footer():
    now_str = datetime.now().strftime("%H:%M:%S  ·  %d %b %Y")
    st.markdown(f"""
    <div style="border-top:2px solid var(--border);
                padding:20px 0 0; margin-top:40px;
                display:flex;justify-content:space-between;align-items:center;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                  color:var(--dim);letter-spacing:0.06em;">
        DBAS v1.0 &nbsp;·&nbsp; DTW + SVM Classification Engine &nbsp;·&nbsp;
        Developed for Fleet Safety Intelligence
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                  color:var(--dim);letter-spacing:0.04em;">
        Last sync: {now_str}
      </div>
    </div>
    """, unsafe_allow_html=True)
