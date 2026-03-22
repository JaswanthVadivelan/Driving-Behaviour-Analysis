import bootstrap
# pages/1_Live_Scoring.py

import os
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from core.scoring.scorer import TripScorer
from core.utils.history_manager import HistoryManager
from core.alerts.alert_engine import AlertEngine
from app.config.theme import (
    apply_theme, render_topbar, render_nav,
    render_page_header, section, stat_chips, page_footer,
    PLOTLY_BASE, AXIS,
)

st.set_page_config(page_title="Live Scoring — DBAS", layout="wide", page_icon="🛡️", initial_sidebar_state="collapsed")
apply_theme()
render_topbar()
render_nav("Live Scoring")
render_page_header(
    "Live Trip Scorer",
    "Upload a speed-profile CSV and get instant aggressive-driving classification",
    badge="DTW · SVM",
)

section("Trip Input")
col_id, col_ds = st.columns([1, 2], gap="small")
with col_id:
    vehicle_id = st.text_input("Vehicle ID", placeholder="e.g. TN 14 AK 3524")
with col_ds:
    project_root = Path(__file__).resolve().parents[2]
    datasets_dir = project_root / "data" / "raw"
    datasets_dir.mkdir(parents=True, exist_ok=True)
    available_files = sorted([f.name for f in datasets_dir.glob("*.csv")])
    selected_dataset = st.selectbox(
        "Select dataset from folder (optional)",
        options=[""] + available_files,
        help="Loads a sample CSV from data/raw",
    )

col_up, col_save = st.columns([3, 1], gap="small")
with col_up:
    uploaded_file = st.file_uploader("Upload CSV — speed_t0 to speed_t49", type=["csv"])
with col_save:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    save_upload = st.checkbox("Save to datasets folder")

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
run_scoring = st.button("▶  Score Trips", type="primary")

if run_scoring:
    if not vehicle_id:
        st.error("Please enter a Vehicle ID before scoring.")
    elif uploaded_file is None and not selected_dataset:
        st.error("Please upload a CSV or select one from the datasets folder.")
    else:
        if selected_dataset:
            input_df = pd.read_csv(datasets_dir / selected_dataset)
        else:
            if save_upload and uploaded_file is not None:
                with open(datasets_dir / uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            input_df = pd.read_csv(uploaded_file)

        speed_cols   = [f"speed_t{i}" for i in range(50)]
        missing_cols = [c for c in speed_cols if c not in input_df.columns]

        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
        else:
            with st.spinner("Analysing driving behaviour…"):
                scorer    = TripScorer()
                scored_df = scorer.score_dataframe(input_df)
                if "trip_id" not in scored_df.columns:
                    scored_df["trip_id"] = [f"trip_{i}" for i in range(len(scored_df))]

            section("Scoring Results")
            n_total = len(scored_df)
            n_calm  = int((scored_df["label"] == "calm").sum())
            n_agg   = int((scored_df["label"] == "aggressive").sum())
            avg_sc  = scored_df["safety_score"].mean()

            k1, k2, k3, k4 = st.columns(4, gap="small")
            with k1:
                st.markdown(f"""
                <div class="kpi blue"><div class="kpi-icon">🚗</div>
                <div class="kpi-label">Total Trips</div><div class="kpi-val">{n_total}</div>
                <div class="kpi-footer"><span class="kpi-sub">Scored this session</span></div></div>
                """, unsafe_allow_html=True)
            with k2:
                st.markdown(f"""
                <div class="kpi green"><div class="kpi-icon">✅</div>
                <div class="kpi-label">Calm Trips</div><div class="kpi-val">{n_calm}</div>
                <div class="kpi-footer"><span class="kpi-sub">Safe behaviour</span></div></div>
                """, unsafe_allow_html=True)
            with k3:
                agg_cls = "red" if n_agg > 0 else "green"
                st.markdown(f"""
                <div class="kpi {agg_cls}"><div class="kpi-icon">⚠️</div>
                <div class="kpi-label">Aggressive Trips</div><div class="kpi-val">{n_agg}</div>
                <div class="kpi-footer"><span class="kpi-sub">Risky behaviour</span></div></div>
                """, unsafe_allow_html=True)
            with k4:
                sc_cls = "green" if avg_sc >= 70 else ("amber" if avg_sc >= 40 else "red")
                st.markdown(f"""
                <div class="kpi {sc_cls}"><div class="kpi-icon">📊</div>
                <div class="kpi-label">Avg Safety Score</div><div class="kpi-val">{avg_sc:.1f}</div>
                <div class="kpi-footer"><span class="kpi-sub">This batch</span></div></div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            section("Trip Analytics")
            ch1, ch2 = st.columns(2, gap="small")

            with ch1:
                st.markdown("""<div class="content-card">
                  <div class="content-card-title">Safety Scores per Trip</div>
                  <div class="content-card-tag">Bar Chart</div></div>""", unsafe_allow_html=True)
                bar_colors = ["#059669" if l == "calm" else "#dc2626" for l in scored_df["label"]]
                fig_bar = go.Figure(go.Bar(
                    x=scored_df["trip_id"], y=scored_df["safety_score"],
                    marker=dict(color=bar_colors, line=dict(width=0)),
                    hovertemplate="<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>",
                ))
                fig_bar.update_layout(
                    **PLOTLY_BASE, height=260,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(title="Trip ID", **AXIS),
                    yaxis=dict(title="Safety Score", range=[0, 105], **AXIS),
                    bargap=0.3,
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with ch2:
                st.markdown("""<div class="content-card">
                  <div class="content-card-title">Classification Split</div>
                  <div class="content-card-tag">Calm vs Aggressive</div></div>""", unsafe_allow_html=True)
                counts = scored_df["label"].value_counts().reset_index()
                counts.columns = ["label", "count"]
                fig_pie = go.Figure(go.Pie(
                    labels=counts["label"], values=counts["count"], hole=0.65,
                    marker=dict(
                        colors=["#059669" if l == "calm" else "#dc2626" for l in counts["label"]],
                        line=dict(color="#ffffff", width=3),
                    ),
                    hovertemplate="<b>%{label}</b><br>%{value} trips — %{percent}<extra></extra>",
                ))
                fig_pie.update_layout(
                    **PLOTLY_BASE, height=260,
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=True,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            section("Detailed Results")
            st.dataframe(
                scored_df[["trip_id", "label", "confidence", "safety_score"]].copy(),
                use_container_width=True, hide_index=True,
                column_config={
                    "trip_id":      st.column_config.TextColumn("Trip ID"),
                    "label":        st.column_config.TextColumn("Label"),
                    "confidence":   st.column_config.NumberColumn("Confidence", format="%.3f"),
                    "safety_score": st.column_config.NumberColumn("Safety Score", format="%.1f"),
                },
            )

            history = HistoryManager()
            history.save_trips(scored_df, vehicle_id)

            alert_engine = AlertEngine()
            alerts = []
            for _, row in scored_df.iterrows():
                alerts.extend(alert_engine.check_trip(vehicle_id, row["label"], row["safety_score"]))

            if alerts:
                section("Triggered Alerts")
                for alert in alerts:
                    st.warning(f"**{alert['alert_type']}** — {alert['message']}")

            section("Export")
            csv_bytes = scored_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇  Download Scored CSV", data=csv_bytes,
                               file_name="scored_trips.csv", mime="text/csv")

page_footer()








