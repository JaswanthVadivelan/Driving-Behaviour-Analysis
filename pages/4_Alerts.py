# pages/4_Alerts.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.alert_engine import AlertEngine
from src.dbas_theme import (
    apply_theme, render_topbar, render_nav,
    render_page_header, section, page_footer,
    PLOTLY_BASE, AXIS,
)

st.set_page_config(page_title="Alerts — DBAS", layout="wide", page_icon="🛡️", initial_sidebar_state="collapsed")
apply_theme()
render_topbar()
render_nav("Alerts")
render_page_header("Alert Management", "Monitor, manage, and resolve safety alerts across the fleet", badge="Alert Engine")

alert_engine  = AlertEngine()
# Always fetch fresh alerts
alerts_df     = alert_engine.get_all_alerts()
active_alerts = alert_engine.get_active_alerts()

n_active   = len(active_alerts) if not active_alerts.empty else 0
n_critical = int((alerts_df["alert_type"] == "Critical Alert").sum()) if not alerts_df.empty else 0
n_resolved = int((alerts_df["status"] == "Resolved").sum()) if not alerts_df.empty and "status" in alerts_df.columns else 0
n_total    = len(alerts_df)

section("Alert Summary")
k1, k2, k3, k4 = st.columns(4, gap="small")
with k1:
    ac = "red" if n_active > 0 else "green"
    st.markdown(f"""
    <div class="kpi {ac}"><div class="kpi-icon">🔔</div>
    <div class="kpi-label">Active Alerts</div><div class="kpi-val">{n_active}</div>
    <div class="kpi-footer"><span class="kpi-sub">Needs Attention</span>
    <span class="kpi-delta {'d-dn' if n_active>0 else 'd-up'}">{'Action needed' if n_active>0 else 'All clear'}</span>
    </div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi red"><div class="kpi-icon">🚨</div>
    <div class="kpi-label">Critical Alerts</div><div class="kpi-val">{n_critical}</div>
    <div class="kpi-footer"><span class="kpi-sub">All time</span></div></div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi green"><div class="kpi-icon">✅</div>
    <div class="kpi-label">Resolved Alerts</div><div class="kpi-val">{n_resolved}</div>
    <div class="kpi-footer"><span class="kpi-sub">All time</span></div></div>
    """, unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="kpi blue"><div class="kpi-icon">📋</div>
    <div class="kpi-label">Total Alerts</div><div class="kpi-val">{n_total}</div>
    <div class="kpi-footer"><span class="kpi-sub">All recorded</span></div></div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

section("Alert Management Board")

if not alerts_df.empty:
    # Filter controls
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        vehicle_filter = st.text_input("Filter by Vehicle ID", placeholder="All vehicles")
    with fc2:
        alert_type_options = sorted(alerts_df["alert_type"].unique().tolist())
        alert_type_filter  = st.multiselect("Filter by Alert Type", options=alert_type_options)
    with fc3:
        status_options = ["Active", "Acknowledged", "Resolved"]
        status_filter = st.multiselect("Filter by Status", options=status_options, default=["Active", "Acknowledged"])
    with fc4:
        severity_options = ["High", "Medium", "Low"]
        valid_options = [s for s in severity_options if "severity" in alerts_df.columns and s in alerts_df["severity"].unique()]
        severity_filter = st.multiselect("Filter by Severity", options=valid_options)

    # Apply filters
    filtered_alerts = alerts_df.copy()
    if vehicle_filter:
        filtered_alerts = filtered_alerts[filtered_alerts["vehicle_id"].str.contains(vehicle_filter, na=False)]
    if alert_type_filter:
        filtered_alerts = filtered_alerts[filtered_alerts["alert_type"].isin(alert_type_filter)]
    if status_filter and "status" in alerts_df.columns:
        filtered_alerts = filtered_alerts[filtered_alerts["status"].isin(status_filter)]
    if severity_filter and "severity" in alerts_df.columns:
        filtered_alerts = filtered_alerts[filtered_alerts["severity"].isin(severity_filter)]

    if "severity" not in filtered_alerts.columns:
        filtered_alerts["severity"] = "Medium"
    if "status" not in filtered_alerts.columns:
        filtered_alerts["status"] = "Active"

    # Display an editable dataframe to manage status
    st.markdown("""
    <div class="content-card">
      <div class="content-card-title">Manage Alerts</div>
      <div class="content-card-tag">Interactive</div>
      <p style="font-size:12px; color:var(--muted);">Edit the 'status' column to acknowledge or resolve alerts.</p>
    </div>
    """, unsafe_allow_html=True)

    cols_to_show = ["alert_id", "vehicle_id", "alert_type", "severity", "timestamp", "status", "message"]
    display_df = filtered_alerts[cols_to_show].copy()

    # Sort so newer and Active alerts show first
    display_df = display_df.sort_values(by=["status", "timestamp"], ascending=[True, False])

    edited_df = st.data_editor(
        display_df,
        column_config={
            "alert_id": st.column_config.TextColumn("Alert ID", disabled=True),
            "vehicle_id": st.column_config.TextColumn("Vehicle ID", disabled=True),
            "alert_type": st.column_config.TextColumn("Type", disabled=True),
            "severity": st.column_config.TextColumn("Severity", disabled=True),
            "timestamp": st.column_config.DatetimeColumn("Timestamp", format="D MMM YYYY, HH:mm", disabled=True),
            "status": st.column_config.SelectboxColumn("Status", options=["Active", "Acknowledged", "Resolved"], required=True),
            "message": st.column_config.TextColumn("Message", disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        key="alert_editor"
    )

    # Check for status changes and apply via alert_engine
    if not display_df.equals(edited_df):
        changed_rows = display_df.compare(edited_df)
        for idx in changed_rows.index:
            alert_id = edited_df.loc[idx, "alert_id"]
            new_status = edited_df.loc[idx, "status"]
            alert_engine.update_alert_status(alert_id, new_status)
        st.success("Alert statuses updated successfully.")
        st.rerun()

else:
    st.info("No alerts found in the system.")

page_footer()
