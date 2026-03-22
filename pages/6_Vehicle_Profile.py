# pages/6_Vehicle_Profile.py

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from src.vehicle_profiler import VehicleProfiler
from src.history_manager import HistoryManager
from src.dbas_theme import (
    apply_theme, render_topbar, render_nav,
    render_page_header, section, page_footer,
    PLOTLY_BASE, AXIS,
)

st.set_page_config(page_title="Vehicle Profile — DBAS", layout="wide", page_icon="🛡️", initial_sidebar_state="collapsed")
apply_theme()
render_topbar()
render_nav("Vehicle Profile")
render_page_header("Vehicle Profile", "Detailed per-vehicle safety analysis, trend tracking and risk summary", badge="Per-Vehicle")

profiler    = VehicleProfiler()
history     = HistoryManager()
vehicle_ids = profiler.get_all_vehicle_ids()

section("Select Vehicle")
selected_vehicle = st.selectbox("Vehicle ID", options=vehicle_ids, placeholder="Choose a vehicle…")

if selected_vehicle:
    profile         = profiler.get_vehicle_profile(selected_vehicle)
    vehicle_history = history.load_history(vehicle_id=selected_vehicle)

    total_trips    = profile.get("total_trips", 0)
    avg_score      = profile.get("avg_safety_score", 0.0)
    pct_aggressive = profile.get("pct_aggressive", 0.0)
    best_trip      = profile.get("best_trip", 0.0)
    worst_trip     = profile.get("worst_trip", 0.0)
    most_common    = profile.get("most_common_label", "N/A")

    section("Vehicle KPIs")
    k1, k2, k3, k4 = st.columns(4, gap="small")
    with k1:
        st.markdown(f"""
        <div class="kpi blue"><div class="kpi-icon">🚗</div>
        <div class="kpi-label">Total Trips</div><div class="kpi-val">{total_trips}</div>
        <div class="kpi-footer"><span class="kpi-sub">Recorded</span></div></div>
        """, unsafe_allow_html=True)
    with k2:
        sc_cls = "green" if avg_score >= 70 else ("amber" if avg_score >= 40 else "red")
        st.markdown(f"""
        <div class="kpi {sc_cls}"><div class="kpi-icon">🛡️</div>
        <div class="kpi-label">Avg Safety Score</div><div class="kpi-val">{avg_score:.1f}</div>
        <div class="kpi-footer"><span class="kpi-sub">All trips</span></div></div>
        """, unsafe_allow_html=True)
    with k3:
        ag_cls = "red" if pct_aggressive > 40 else ("amber" if pct_aggressive > 20 else "green")
        st.markdown(f"""
        <div class="kpi {ag_cls}"><div class="kpi-icon">⚠️</div>
        <div class="kpi-label">Aggressive %</div>
        <div class="kpi-val">{pct_aggressive:.1f}<span style="font-size:18px;font-weight:600">%</span></div>
        <div class="kpi-footer"><span class="kpi-sub">Risky trips</span></div></div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi amber"><div class="kpi-icon">📊</div>
        <div class="kpi-label">Best / Worst Trip</div>
        <div class="kpi-val" style="font-size:26px">{best_trip:.1f}
          <span style="opacity:0.35;font-size:18px;font-weight:400"> / </span>{worst_trip:.1f}
        </div>
        <div class="kpi-footer"><span class="kpi-sub">Score range</span></div></div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    section("Driving Analysis")

    if vehicle_history is not None and not vehicle_history.empty:
        ch1, ch2 = st.columns(2, gap="small")

        with ch1:
            st.markdown("""<div class="content-card">
              <div class="content-card-title">Safety Score Trend</div>
              <div class="content-card-tag">Over time</div></div>""", unsafe_allow_html=True)
            trend_df = vehicle_history.copy()
            trend_df["timestamp"] = pd.to_datetime(trend_df["timestamp"], errors="coerce")
            trend_df = trend_df.dropna(subset=["timestamp"]).sort_values("timestamp")
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=trend_df["timestamp"], y=trend_df["safety_score"],
                fill="tozeroy", fillcolor="rgba(26,86,219,0.05)",
                line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
            ))
            fig_line.add_trace(go.Scatter(
                x=trend_df["timestamp"], y=trend_df["safety_score"],
                mode="lines+markers",
                line=dict(color="#1a56db", width=2.5, shape="spline", smoothing=0.85),
                marker=dict(size=6, color="#1a56db", line=dict(color="#ffffff", width=2)),
                hovertemplate="<b>%{x|%d %b %H:%M}</b><br>Score: %{y:.1f}<extra></extra>",
                showlegend=False,
            ))
            fig_line.add_hline(y=70, line_dash="dash", line_color="rgba(5,150,105,0.5)",
                               line_width=1.5, annotation_text="Safe threshold",
                               annotation_font_size=10, annotation_font_color="rgba(5,150,105,0.8)")
            fig_line.update_layout(
                **PLOTLY_BASE, height=260,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(title="", **AXIS),
                yaxis=dict(title="Safety Score", range=[0, 105], **AXIS),
                hovermode="x unified",
            )
            st.plotly_chart(fig_line, use_container_width=True)

        with ch2:
            st.markdown("""<div class="content-card">
              <div class="content-card-title">Aggressive Trip %</div>
              <div class="content-card-tag">Risk gauge</div></div>""", unsafe_allow_html=True)
            needle = "#059669" if pct_aggressive < 20 else ("#d97706" if pct_aggressive < 50 else "#dc2626")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pct_aggressive,
                number=dict(font=dict(family="'Plus Jakarta Sans', sans-serif", size=42, color=needle), suffix="%"),
                title=dict(text="Aggressive Trip Percentage",
                           font=dict(family="'Plus Jakarta Sans', sans-serif", size=13, color="#0f172a")),
                gauge=dict(
                    axis=dict(range=[0, 100],
                              tickfont=dict(family="'DM Sans', sans-serif", size=10, color="#94a3b8")),
                    bar=dict(color=needle, thickness=0.24),
                    bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    steps=[
                        dict(range=[0,  33], color="rgba(5,150,105,0.07)"),
                        dict(range=[33, 66], color="rgba(217,119,6,0.07)"),
                        dict(range=[66,100], color="rgba(220,38,38,0.07)"),
                    ],
                ),
            ))
            fig_gauge.update_layout(
                **PLOTLY_BASE, height=260,
                margin=dict(l=20, r=20, t=40, b=10),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.info("No trip history available for this vehicle yet.")

    section("Driving Summary")
    if total_trips == 0:
        st.info("No trip data available to summarise this vehicle.")
    else:
        if avg_score < 40 or pct_aggressive > 60:
            risk_level = "🔴 High Risk"
            risk_color = "var(--red)"
            risk_bg    = "var(--red-light)"
            risk_border= "rgba(220,38,38,0.2)"
            risk_text  = "High-risk driving patterns detected. Immediate coaching or intervention recommended."
        elif avg_score < 70 or pct_aggressive > 35:
            risk_level = "🟡 Moderate Risk"
            risk_color = "var(--amber)"
            risk_bg    = "var(--amber-light)"
            risk_border= "rgba(217,119,6,0.2)"
            risk_text  = "Moderate risk patterns observed. Monitoring and targeted coaching advised."
        else:
            risk_level = "🟢 Low Risk"
            risk_color = "var(--green)"
            risk_bg    = "var(--green-light)"
            risk_border= "rgba(5,150,105,0.2)"
            risk_text  = "Driving behaviour appears safe and consistent. Continue monitoring."

        st.markdown(f"""
        <div class="content-card" style="background:{risk_bg};border-color:{risk_border};">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
            <div style="font-family:var(--font-d);font-size:15px;font-weight:800;color:{risk_color};">
              {risk_level}
            </div>
            <div style="font-family:var(--font-m);font-size:9px;letter-spacing:0.1em;text-transform:uppercase;
                        color:var(--muted);padding:3px 12px;border:1px solid var(--border);
                        border-radius:20px;background:var(--surface);">
              {selected_vehicle}
            </div>
          </div>
          <div style="font-family:var(--font-b);font-size:13.5px;color:var(--text-2);line-height:1.7;">
            Vehicle <strong style="color:var(--text)">{selected_vehicle}</strong> has
            <strong style="color:var(--text)">{total_trips}</strong> recorded trips.
            The most common driving label is <strong style="color:var(--text)">{most_common}</strong>,
            with an average safety score of
            <strong style="color:{risk_color}">{avg_score:.1f}</strong> and
            <strong style="color:{risk_color}">{pct_aggressive:.1f}%</strong> aggressive trips.
            {risk_text}
          </div>
        </div>
        """, unsafe_allow_html=True)

    if vehicle_history is not None and not vehicle_history.empty:
        section("Full Trip Log")
        st.dataframe(vehicle_history, use_container_width=True, hide_index=True)
else:
    st.info("Select a vehicle from the dropdown above to view its profile.")

page_footer()
