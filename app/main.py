import bootstrap

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from core.utils.config import Config
from core.utils.history_manager import HistoryManager
from core.alerts.alert_engine import AlertEngine
from core.profiling.vehicle_profiler import VehicleProfiler
from app.config.theme import (
    apply_theme, render_topbar, render_nav,
    render_page_header, section, page_footer,
    get_plotly_layout, get_axis_layout
)
from app.components.kpi_card import render_kpi_card
from app.components.chart_card import render_chart_card

st.set_page_config(
    page_title="DBAS — Fleet Intelligence",
    layout="wide", page_icon="🛡️",
    initial_sidebar_state="collapsed",
)
apply_theme()
render_topbar()
render_nav("Dashboard")
render_page_header(
    "Fleet Dashboard",
    "Real-time aggressive driving detection · DTW feature extraction · SVM classification",
    badge="v1.0 · Fleet Monitor",
)

# ── Init ──────────────────────────────────────────────────────────────────────────
cfg             = Config.load()
history_manager = HistoryManager()
alert_engine    = AlertEngine()
vehicle_profiler = VehicleProfiler()

summary       = history_manager.get_summary_stats()
active_alerts = alert_engine.get_active_alerts()
history_df    = history_manager.load_history()

total_trips    = summary.get("total_trips", 0)
avg_score      = summary.get("avg_safety_score", 0.0)
pct_aggressive = summary.get("pct_aggressive", 0.0)
n_alerts       = int(active_alerts.shape[0]) if active_alerts is not None else 0

# ── KPI Cards ─────────────────────────────────────────────────────────────────────
section("Key Performance Indicators")

# KPI Cards logic in components/kpi_card.py handles html structure rendering
c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    render_kpi_card("Total Trips", f"{total_trips:,}", "All recorded trips", "↑ Active", "d-up", "blue", "🚗", delay=0.05)

with c2:
    sc_cls = "green" if avg_score >= 70 else ("amber" if avg_score >= 40 else "red")
    sc_delta = "d-up" if avg_score >= 70 else ("d-neu" if avg_score >= 40 else "d-dn")
    sc_text = 'Safe' if avg_score>=70 else 'Moderate' if avg_score>=40 else 'At Risk'
    render_kpi_card("Fleet Safety Score", f"{avg_score:.1f}", "Fleet average", sc_text, sc_delta, sc_cls, "🛡️", delay=0.10)

with c3:
    al_cls = "red" if n_alerts > 5 else ("amber" if n_alerts > 0 else "green")
    al_delta = "d-dn" if n_alerts > 5 else ("d-neu" if n_alerts > 0 else "d-up")
    al_text = 'High' if n_alerts>5 else 'Review' if n_alerts>0 else 'Clear'
    render_kpi_card("Active Alerts", str(n_alerts), "Last 24 hours", al_text, al_delta, al_cls, "⚠️", delay=0.15)

with c4:
    ag_cls = "red" if pct_aggressive > 25 else ("amber" if pct_aggressive > 10 else "green")
    ag_delta = "d-dn" if pct_aggressive > 25 else ("d-neu" if pct_aggressive > 10 else "d-up")
    ag_text = 'High Risk' if pct_aggressive>25 else 'Moderate' if pct_aggressive>10 else 'Low Risk'
    render_kpi_card("Aggressive %", f"{pct_aggressive:.1f}%", "Share of risky trips", ag_text, ag_delta, ag_cls, "📊", delay=0.20)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── AI Fleet Intelligence Insights ────────────────────────────────────────────────
section("AI Insights")
if history_df is not None and not history_df.empty:
    Insights_msgs = []
    
    # Highest risk vehicle
    risk_veh = history_df[history_df["label"] == "aggressive"].groupby("vehicle_id").size().sort_values(ascending=False)
    if not risk_veh.empty:
        worst_v = risk_veh.index[0]
        v_trips = history_df[history_df["vehicle_id"]==worst_v]
        v_pct = (risk_veh.iloc[0] / len(v_trips)) * 100
        if v_pct > 20:
            Insights_msgs.append(f"Vehicle {worst_v} shows {v_pct:.0f}% aggressive trips. Review driving patterns.")
            
    # Trend
    history_timestamps = pd.to_datetime(history_df["timestamp"], errors="coerce").dt.tz_localize(None)
    last_week = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=7)
    
    df_recent = history_df[history_timestamps >= last_week]
    df_older = history_df[history_timestamps < last_week]
    
    if len(df_recent) > 10 and len(df_older) > 10:
        recent_risk = (df_recent["label"] == "aggressive").mean() * 100
        older_risk = (df_older["label"] == "aggressive").mean() * 100
        delta = recent_risk - older_risk
        if delta > 5:
            Insights_msgs.append(f"Fleet risk increased by {delta:.1f}% this week.")
        elif delta < -5:
            Insights_msgs.append(f"Fleet safety improved. Aggressive driving dropped by {abs(delta):.1f}% this week.")
            
    # Safest vehicle improvement (mock)
    safe_veh = history_df.groupby("vehicle_id")["safety_score"].mean().sort_values(ascending=False)
    if not safe_veh.empty:
        best_v = safe_veh.index[0]
        Insights_msgs.append(f"Vehicle {best_v} is leading with highest average safety score ({safe_veh.iloc[0]:.0f}).")
        
    for msg in Insights_msgs:
        st.markdown(f"""
        <div style="background:var(--blue-light); border-left:4px solid var(--blue); padding:16px; border-radius:8px; margin-bottom:12px; box-shadow:var(--shadow-sm); display:flex; align-items:center; gap:12px;">
            <div style="font-size:20px;">💡</div>
            <div style="color:var(--text); font-weight:500; font-family:'DM Sans', sans-serif;">{msg}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Gathering data for AI Insights...")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────────────────────────────────────────
section("Fleet Analytics")

row1a, row1b = st.columns([1, 2], gap="small")

with row1a:
    st.markdown("""
    <div class="content-card">
      <div class="content-card-title">Trip Classification</div>
      <div class="content-card-tag">Calm vs Aggressive</div>
    </div>""", unsafe_allow_html=True)

    if history_df is not None and not history_df.empty and "label" in history_df.columns:
        lc = history_df["label"].value_counts().reset_index()
        lc.columns = ["label", "count"]
        total = lc["count"].sum()
        calm_count = lc[lc["label"] == "calm"]["count"].values
        calm_pct = (calm_count[0] / total * 100) if len(calm_count) else 0

        fig_pie = go.Figure(go.Pie(
            labels=lc["label"], values=lc["count"],
            hole=0.65,
            marker=dict(
                colors=["#059669" if l == "calm" else "#dc2626" for l in lc["label"]],
                line=dict(color="rgba(0,0,0,0)", width=2),
            ),
            hovertemplate="<b>%{label}</b><br>%{value:,} trips — %{percent}<extra></extra>",
        ))
        fig_pie.add_annotation(
            text=f"<b>{calm_pct:.1f}%</b><br><span style='font-size:10px'>CALM</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(family="'Plus Jakarta Sans', sans-serif", size=20, color="#64748b"),
            align="center",
        )
        pie_layout = {
            **get_plotly_layout(),
            "legend": dict(
                orientation="v",
                x=1.04,
                y=0.5,
                font=dict(family="'DM Sans', sans-serif", size=11, color="#64748b"),
            ),
        }
        fig_pie.update_layout(
            **pie_layout,
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Trip classification will appear once history is available.")

with row1b:
    st.markdown("""
    <div class="content-card">
      <div class="content-card-title">Safety Score Trend</div>
      <div class="content-card-tag">Rolling window</div>
    </div>""", unsafe_allow_html=True)
    
    if history_df is not None and not history_df.empty and "safety_score" in history_df.columns:
        trend = history_df.copy()
        trend["timestamp"] = pd.to_datetime(trend["timestamp"], errors="coerce")
        trend = trend.dropna(subset=["timestamp"]).sort_values("timestamp")
    
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=trend["timestamp"], y=trend["safety_score"],
            fill="tozeroy", fillcolor="rgba(26,86,219,0.05)",
            line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
        ))
        fig_line.add_trace(go.Scatter(
            x=trend["timestamp"], y=trend["safety_score"],
            mode="lines+markers",
            line=dict(color="#1a56db", width=2.5, shape="spline", smoothing=0.85),
            marker=dict(size=5, color="#1a56db", line=dict(color="#ffffff", width=2)),
            hovertemplate="<b>%{x|%d %b %H:%M}</b><br>Score: %{y:.1f}<extra></extra>",
            showlegend=False,
        ))
        fig_line.add_hline(
            y=70, line_dash="dash", line_color="rgba(5,150,105,0.5)", line_width=1.5,
            annotation_text="Safe threshold (70)",
            annotation_font_size=10, annotation_font_color="rgba(5,150,105,0.8)",
        )
        fig_line.update_layout(
            **get_plotly_layout(), height=240,
            margin=dict(l=10, r=10, t=14, b=10),
            xaxis=dict(title="", **get_axis_layout()),
            yaxis=dict(title="Safety Score", range=[0, 105], **get_axis_layout()),
            hovermode="x unified",
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Safety score trend will appear once trip history is available.")

# ── Recent Alerts ─────────────────────────────────────────────────────────────────
section("Recent Alerts")

n_str = f"{n_alerts} alert{'s' if n_alerts != 1 else ''}"
st.markdown(f"""
<div style="background:var(--surface);border:1px solid var(--border);
            border-radius:var(--radius-xl);overflow:hidden;box-shadow:var(--shadow-sm);">
  <div style="display:flex;align-items:center;justify-content:space-between;
              padding:16px 24px;border-bottom:1px solid var(--border);
              background:var(--surface2);">
    <div style="font-family:var(--font-d);font-size:14px;font-weight:700;color:var(--text);
                display:flex;align-items:center;gap:10px;">
      Active Alerts — Last 24 Hours
      <span style="font-family:var(--font-m);font-size:10px;font-weight:600;
                   padding:3px 10px;border-radius:20px;
                   background:{'var(--red-light)' if n_alerts>0 else 'var(--green-light)'};
                   border:1px solid {'rgba(220,38,38,0.2)' if n_alerts>0 else 'rgba(5,150,105,0.2)'};
                   color:{'var(--red)' if n_alerts>0 else 'var(--green)'};">
        {n_str}
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if active_alerts is not None and not active_alerts.empty:
    st.dataframe(active_alerts, width="stretch", hide_index=True)
else:
    st.markdown("""
    <div style="background:var(--green-light);border:1px solid rgba(5,150,105,0.2);
                border-radius:var(--radius-lg);padding:24px;text-align:center;margin-top:8px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                  letter-spacing:0.1em;text-transform:uppercase;color:var(--green);">
        ✓ &nbsp; No active alerts in the last 24 hours
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Gauge ─────────────────────────────────────────────────────────────────────────
section("Fleet Health Score")

fleet_avg    = summary.get("avg_safety_score", 0.0)
needle_color = "#059669" if fleet_avg >= 70 else ("#d97706" if fleet_avg >= 40 else "#dc2626")

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=fleet_avg,
    delta=dict(
        reference=70,
        increasing=dict(color="#059669"),
        decreasing=dict(color="#dc2626"),
        font=dict(family="'DM Sans', sans-serif", size=13),
    ),
    number=dict(
        font=dict(family="'Plus Jakarta Sans', sans-serif", size=52, color=needle_color),
    ),
    title=dict(
        text="Fleet Average Safety Score",
        font=dict(family="'Plus Jakarta Sans', sans-serif", size=14, color="#0f172a"),
    ),
    gauge=dict(
        axis=dict(
            range=[0, 100],
            tickfont=dict(family="'DM Sans', sans-serif", size=10, color="#94a3b8"),
            nticks=11,
        ),
        bar=dict(color=needle_color, thickness=0.24),
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        steps=[
            dict(range=[0,  40], color="rgba(220,38,38,0.06)"),
            dict(range=[40, 70], color="rgba(217,119,6,0.06)"),
            dict(range=[70,100], color="rgba(5,150,105,0.06)"),
        ],
        threshold=dict(
            line=dict(color=needle_color, width=2),
            thickness=0.8, value=fleet_avg,
        ),
    ),
))
fig_gauge.update_layout(
    **get_plotly_layout(), height=300,
    margin=dict(l=30, r=30, t=50, b=20),
)

_, gcol, _ = st.columns([1, 2, 1])
with gcol:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.plotly_chart(fig_gauge, width="stretch")
    st.markdown("""
    <div style="display:flex;justify-content:center;gap:24px;padding:0 0 10px;
                font-family:'JetBrains Mono',monospace;font-size:10px;">
      <span style="color:#dc2626;">● 0–40 Critical</span>
      <span style="color:#d97706;">● 40–70 Moderate</span>
      <span style="color:#059669;">● 70–100 Safe</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

page_footer()





