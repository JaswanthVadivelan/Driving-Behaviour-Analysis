# src/dbas_theme.py
# Professional white/light conference theme for DBAS.

import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu

# ── Navigation constants ──────────────────────────────────────────────────────────
NAV_OPTIONS  = ["Dashboard", "Live Scoring", "Driver Leaderboard", "Model Performance", "Vehicle Profile", "Alerts", "Reports"]
NAV_ICONS    = ["grid", "speedometer2", "trophy", "graph-up", "person-badge", "exclamation-triangle", "file-earmark-bar-graph"]
NAV_PAGE_MAP = {
    "Dashboard":          "main.py",
    "Live Scoring":       "pages/01_live_scoring.py",
    "Driver Leaderboard": "pages/05_driver_leaderboard.py",
    "Model Performance":  "pages/06_model_performance.py",
    "Vehicle Profile":    "pages/04_vehicle_profile.py",
    "Alerts":             "pages/02_alerts.py",
    "Reports":            "pages/03_reports.py",
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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --bg:          #f0f4f8;
  --surface:     rgba(255, 255, 255, 0.75);
  --surface2:    rgba(255, 255, 255, 0.5);
  --surface3:    rgba(255, 255, 255, 0.2);

  --border:      rgba(255, 255, 255, 0.6);
  --border-med:  rgba(255, 255, 255, 0.9);

  --text:        #0f172a;
  --text-2:      #334155;
  --muted:       #64748b;
  --dim:         #94a3b8;

  --blue:        #2563eb;
  --blue-light:  rgba(37, 99, 235, 0.1);
  --blue-mid:    rgba(37, 99, 235, 0.2);
  --blue-grad:   linear-gradient(135deg, #2563eb, #7c3aed);

  --green:       #059669;
  --green-light: rgba(5, 150, 105, 0.1);
  --green-grad:  linear-gradient(135deg, #059669, #10b981);

  --amber:       #d97706;
  --amber-light: rgba(217, 119, 6, 0.1);
  --amber-grad:  linear-gradient(135deg, #d97706, #f59e0b);

  --red:         #dc2626;
  --red-light:   rgba(220, 38, 38, 0.1);
  --red-grad:    linear-gradient(135deg, #dc2626, #ef4444);

  --font-d:  'Outfit', sans-serif;
  --font-b:  'Inter', sans-serif;
  --font-m:  'Space Grotesk', monospace;

  --radius:    14px;
  --radius-lg: 20px;
  --radius-xl: 28px;

  --shadow-sm: 0 4px 15px rgba(0,0,0,0.03);
  --shadow:    0 10px 40px rgba(0,0,0,0.08);
  --shadow-lg: 0 20px 50px rgba(0,0,0,0.12);

  --glass-blur: blur(24px);
  --glass-border: 1px solid rgba(255, 255, 255, 0.7);
}

html, body, [class*="css"] {
  font-family: var(--font-b) !important;
  color: var(--text) !important;
}

.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: radial-gradient(circle at 10% 20%, rgba(37, 99, 235, 0.08) 0%, transparent 40%),
              radial-gradient(circle at 90% 80%, rgba(124, 58, 237, 0.08) 0%, transparent 40%),
              radial-gradient(circle at 50% 50%, rgba(5, 150, 105, 0.04) 0%, transparent 60%),
              var(--bg) !important;
  background-attachment: fixed !important;
}

section[data-testid="stSidebar"]  { display: none !important; }
div[data-testid="stSidebarNav"]   { display: none !important; }
#MainMenu, footer, header         { visibility: hidden !important; }
.block-container {
  padding: 0 3rem 4rem !important;
  max-width: 100% !important;
}

.dbas-topbar {
  position: sticky; top: 0; z-index: 999;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 3rem;
  height: 70px;
  background: var(--surface);
  border-bottom: var(--glass-border);
  backdrop-filter: var(--glass-blur);
  margin: 0 -3rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}
.dbas-brand { display: flex; align-items: center; gap: 14px; }
.dbas-logo {
  width: 42px; height: 42px;
  background: var(--blue-grad);
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.dbas-logo:hover { transform: rotate(8deg) scale(1.08); }
.dbas-logo svg { width: 22px; height: 22px; }
.dbas-brand-name {
  font-family: var(--font-d); font-size: 20px; font-weight: 800;
  letter-spacing: -0.02em; color: var(--text); line-height: 1.1;
  background: linear-gradient(90deg, #0f172a, #2563eb);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.dbas-brand-sub {
  font-family: var(--font-m); font-size: 11px; color: var(--muted);
  letter-spacing: 0.12em; text-transform: uppercase; font-weight: 600;
}
.dbas-live {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-m); font-size: 11px; font-weight: 600;
  letter-spacing: 0.1em; color: var(--green); text-transform: uppercase;
  background: var(--green-light);
  padding: 8px 16px; border-radius: 20px;
  border: 1px solid rgba(5, 150, 105, 0.2);
  backdrop-filter: var(--glass-blur);
}
.dbas-live-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--green); box-shadow: 0 0 10px rgba(5, 150, 105, 0.8);
  animation: pulseLive 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulseLive { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.7); } }
.dbas-time {
  font-family: var(--font-m); font-size: 12px; font-weight: 600;
  color: var(--text-2); letter-spacing: 0.05em;
  background: var(--surface2); padding: 8px 16px;
  border-radius: 12px; border: var(--glass-border);
  backdrop-filter: var(--glass-blur);
}

.dbas-page-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  padding: 36px 0 24px;
  margin-bottom: 32px;
  position: relative;
}
.dbas-page-header::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--border), transparent);
}
.dbas-page-title {
  font-family: var(--font-d); font-size: 38px; font-weight: 800;
  letter-spacing: -0.03em; color: var(--text);
  line-height: 1.1; margin-bottom: 4px;
}
.dbas-page-sub {
  font-size: 15px; color: var(--text-2);
  font-weight: 400; font-family: var(--font-b);
}
.dbas-badge {
  font-family: var(--font-m); font-size: 11px; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase;
  padding: 8px 18px; border-radius: 24px;
  background: var(--surface); backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  color: var(--blue);
  box-shadow: var(--shadow-sm);
}

.dbas-section {
  display: flex; align-items: center; gap: 14px;
  font-family: var(--font-m); font-size: 11px;
  letter-spacing: 0.15em; text-transform: uppercase;
  color: var(--muted); margin: 40px 0 24px;
  font-weight: 700;
}
.dbas-section::after {
  content: ''; flex: 1; height: 1px; 
  background: linear-gradient(90deg, var(--border-med), transparent);
}

.kpi {
  background: var(--surface);
  backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-xl);
  padding: 28px;
  position: relative; overflow: hidden;
  border: var(--glass-border);
  box-shadow: var(--shadow-sm);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: default;
  animation: floatUp 0.6s ease-out both;
}
.kpi:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-6px) scale(1.02);
  border-color: var(--border-med);
}
.kpi::before {
  content: ''; position: absolute;
  top: 0; left: 0; right: 0; height: 5px;
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  opacity: 0.9;
}
.kpi.blue::before  { background: var(--blue-grad); }
.kpi.green::before { background: var(--green-grad); }
.kpi.amber::before { background: var(--amber-grad); }
.kpi.red::before   { background: var(--red-grad); }

.kpi-icon {
  width: 50px; height: 50px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px; font-size: 24px;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.kpi:hover .kpi-icon { transform: scale(1.15) rotate(10deg); }
.blue  .kpi-icon { background: var(--blue-light); color: var(--blue); }
.green .kpi-icon { background: var(--green-light); color: var(--green); }
.amber .kpi-icon { background: var(--amber-light); color: var(--amber); }
.red   .kpi-icon { background: var(--red-light); color: var(--red); }

.kpi-label {
  font-family: var(--font-m); font-size: 11px;
  letter-spacing: 0.15em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 10px; font-weight: 700;
}
.kpi-val {
  font-family: var(--font-d); font-size: 44px; font-weight: 800;
  line-height: 1; letter-spacing: -0.04em; 
  text-shadow: 0 4px 15px rgba(0,0,0,0.05);
}
.blue  .kpi-val { background: var(--blue-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.green .kpi-val { background: var(--green-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.amber .kpi-val { background: var(--amber-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.red   .kpi-val { background: var(--red-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

.kpi-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 18px; padding-top: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}
.kpi-sub  { font-size: 13px; color: var(--text-2); font-weight: 500; }
.kpi-delta {
  font-family: var(--font-m); font-size: 11px;
  padding: 5px 12px; border-radius: 20px; font-weight: 700; letter-spacing: 0.05em;
  box-shadow: var(--shadow-sm);
}
.d-up  { background: var(--green-light); color: var(--green); border: var(--glass-border); }
.d-dn  { background: var(--red-light);   color: var(--red);   border: var(--glass-border); }
.d-neu { background: var(--amber-light); color: var(--amber); border: var(--glass-border); }

.content-card {
  background: var(--surface);
  backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  border-radius: var(--radius-xl);
  padding: 28px 32px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  animation: floatUp 0.6s ease-out both;
}
.content-card:hover {
  box-shadow: var(--shadow);
  border-color: var(--border-med);
  transform: translateY(-3px);
}
.content-card-title {
  font-family: var(--font-d); font-size: 18px; font-weight: 800;
  letter-spacing: -0.02em; color: var(--text); margin-bottom: 8px;
}
.content-card-tag {
  font-family: var(--font-m); font-size: 11px; color: var(--muted);
  letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700;
  display: inline-block; padding: 5px 12px;
  border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 20px;
  margin-bottom: 16px; background: var(--surface2);
}

[data-testid="stTextInput"] input {
  background: var(--surface) !important;
  backdrop-filter: var(--glass-blur) !important;
  border: var(--glass-border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--font-b) !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  padding: 12px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stSelectbox"] > div > div:focus-within {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 4px var(--blue-light), var(--shadow) !important;
  transform: translateY(-2px);
}
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stFileUploader"] label,
[data-testid="stCheckbox"] label {
  font-family: var(--font-m) !important;
  font-size: 12px !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--text-2) !important;
  font-weight: 700 !important;
  margin-bottom: 6px !important;
}

[data-testid="stButton"] > button {
  background: var(--surface) !important;
  backdrop-filter: var(--glass-blur) !important;
  border: var(--glass-border) !important;
  color: var(--text) !important;
  border-radius: var(--radius) !important;
  font-family: var(--font-m) !important;
  font-size: 14px !important;
  font-weight: 700 !important;
  letter-spacing: 0.05em !important;
  padding: 12px 28px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
[data-testid="stButton"] > button:hover {
  border-color: var(--blue) !important;
  color: var(--blue) !important;
  background: var(--surface2) !important;
  box-shadow: var(--shadow) !important;
  transform: translateY(-3px) scale(1.02);
}
[data-testid="stButton"] > button[kind="primary"] {
  background: var(--blue-grad) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3) !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
  box-shadow: 0 12px 35px rgba(37, 99, 235, 0.4) !important;
  transform: translateY(-3px) scale(1.04);
}

[data-testid="stDataFrame"] > div {
  background: var(--surface) !important;
  backdrop-filter: var(--glass-blur) !important;
  border: var(--glass-border) !important;
  border-radius: var(--radius-xl) !important;
  box-shadow: var(--shadow-sm) !important;
}

[data-testid="stInfo"] {
  background: var(--blue-light) !important;
  border: var(--glass-border) !important;
  border-left: 4px solid var(--blue) !important;
  border-radius: var(--radius) !important;
  color: var(--blue) !important;
  font-family: var(--font-b) !important;
  backdrop-filter: var(--glass-blur) !important;
}
[data-testid="stWarning"] {
  background: var(--amber-light) !important;
  border: var(--glass-border) !important;
  border-left: 4px solid var(--amber) !important;
  border-radius: var(--radius) !important;
  color: var(--amber) !important;
  font-family: var(--font-b) !important;
  backdrop-filter: var(--glass-blur) !important;
}
[data-testid="stError"] {
  background: var(--red-light) !important;
  border: var(--glass-border) !important;
  border-left: 4px solid var(--red) !important;
  border-radius: var(--radius) !important;
  color: var(--red) !important;
  font-family: var(--font-b) !important;
  backdrop-filter: var(--glass-blur) !important;
}
[data-testid="stSuccess"] {
  background: var(--green-light) !important;
  border: var(--glass-border) !important;
  border-left: 4px solid var(--green) !important;
  border-radius: var(--radius) !important;
  color: var(--green) !important;
  font-family: var(--font-b) !important;
  backdrop-filter: var(--glass-blur) !important;
}

.dbas-alert-card {
  background: var(--surface);
  backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 18px 24px;
  margin-bottom: 12px;
  display: flex; gap: 16px; align-items: flex-start;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  animation: floatUp 0.5s ease-out both;
}
.dbas-alert-card:hover { box-shadow: var(--shadow); transform: translateX(4px); }
.dbas-alert-card.critical { border-left: 4px solid var(--red); background: var(--red-light); }
.dbas-alert-card.warning { border-left: 4px solid var(--amber); background: var(--amber-light); }

.dbas-alert-icon {
  width: 40px; height: 40px; flex-shrink: 0;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
}
.dbas-alert-icon.critical { background: rgba(220,38,38,0.15); color: var(--red); }
.dbas-alert-icon.warning  { background: rgba(217,119,6,0.15); color: var(--amber); }

.dbas-alert-body-title {
  font-family: var(--font-d); font-size: 15px; font-weight: 800;
  color: var(--text); margin-bottom: 6px;
}

h1, h2, h3 {
  font-family: var(--font-d) !important;
  font-weight: 800 !important;
  color: var(--text) !important;
  letter-spacing: -0.02em !important;
}
p { font-family: var(--font-b) !important; color: var(--text-2) !important; font-size: 15px !important; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.3); border-radius: 4px; border: 2px solid var(--bg); }
::-webkit-scrollbar-thumb:hover { background: rgba(148, 163, 184, 0.8); }

@keyframes floatUp {
  from { opacity: 0; transform: translateY(24px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
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
  --bg:          #050814;
  --surface:     rgba(15, 23, 42, 0.6);
  --surface2:    rgba(30, 41, 59, 0.5);
  --surface3:    rgba(51, 65, 85, 0.4);

  --border:      rgba(255, 255, 255, 0.08);
  --border-med:  rgba(255, 255, 255, 0.15);

  --text:        #f8fafc;
  --text-2:      #cbd5e1;
  --muted:       #94a3b8;
  --dim:         #64748b;

  --blue:        #3b82f6;
  --blue-grad:   linear-gradient(135deg, #60a5fa, #3b82f6);

  --shadow-sm:   0 4px 15px rgba(0,0,0,0.4);
  --shadow:      0 10px 40px rgba(0,0,0,0.6);
  --shadow-lg:   0 20px 50px rgba(0,0,0,0.8);

  --glass-border: 1px solid rgba(255, 255, 255, 0.1);
}

.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: radial-gradient(circle at 15% 20%, rgba(37, 99, 235, 0.15) 0%, transparent 45%),
              radial-gradient(circle at 85% 80%, rgba(124, 58, 237, 0.15) 0%, transparent 45%),
              radial-gradient(circle at 50% 50%, rgba(5, 150, 105, 0.05) 0%, transparent 65%),
              #050814 !important;
  background-attachment: fixed !important;
  color: var(--text) !important;
}

.dbas-topbar {
  background: rgba(5, 8, 20, 0.7) !important;
}
.dbas-brand-name {
  background: linear-gradient(90deg, #f8fafc, #60a5fa);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.kpi.blue::before  { background: linear-gradient(90deg, #93c5fd, #60a5fa); }
.blue .kpi-val { background: linear-gradient(90deg, #93c5fd, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.blue .kpi-icon { background: rgba(96, 165, 250, 0.15); color: #93c5fd; }
.dbas-badge { background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(147, 197, 253, 0.3); }

/* Overrides for Metric cards in Dark Mode */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  backdrop-filter: var(--glass-blur) !important;
  border: var(--glass-border) !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stMetricValue"] {
  color: var(--text) !important;
}
</style>
"""

def apply_theme():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    if st.session_state.get('theme', 'Light') == 'Dark':
        st.markdown(DARK_MODE_OVERRIDES, unsafe_allow_html=True)


def render_topbar():
    now_str = datetime.now().strftime("%H:%M:%S  ?  %d %b %Y")
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
    now_str = datetime.now().strftime("%H:%M:%S  ?  %d %b %Y")
    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        st.markdown(f"""
        <div style="border-top:2px solid var(--border);
                    padding:20px 0 0; margin-top:40px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                      color:var(--dim);letter-spacing:0.06em;">
            DBAS v1.0 &nbsp;?&nbsp; DTW + SVM Classification Engine &nbsp;?&nbsp;
            Developed for Fleet Safety Intelligence
          </div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                      color:var(--dim);letter-spacing:0.04em; margin-top:6px;">
            Last sync: {now_str}
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)


