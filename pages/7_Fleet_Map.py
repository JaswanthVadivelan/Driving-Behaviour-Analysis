import streamlit as st
import pandas as pd
import numpy as np

from src.history_manager import HistoryManager
from src.dbas_theme import apply_theme, render_topbar, render_nav, render_page_header, page_footer
from components.map_view import render_fleet_map

st.set_page_config(page_title="Fleet Map", layout="wide", page_icon="🗺️", initial_sidebar_state="collapsed")
apply_theme()
render_topbar()
render_nav("Fleet Map")
render_page_header("Fleet Map", "Real-time geographical vehicle tracking", badge="v1.0 · Live")

history_manager = HistoryManager()
history_df = history_manager.load_history()

if history_df.empty:
    st.info("No trip history available to generate the map.")
else:
    # Summarize history per vehicle
    vehicle_stats = history_df.groupby("vehicle_id").agg(
        safety_score=('safety_score', 'mean'),
        trips=('trip_id', 'count'),
        aggressive=('label', lambda x: (x == 'aggressive').sum())
    ).reset_index()

    # Simulate GPS data using a fixed center point (e.g., San Francisco)
    np.random.seed(42)  # For consistent simulation
    center_lat, center_lon = 37.7749, -122.4194

    vehicle_stats["lat"] = center_lat + np.random.uniform(-0.1, 0.1, len(vehicle_stats))
    vehicle_stats["lon"] = center_lon + np.random.uniform(-0.1, 0.1, len(vehicle_stats))
    
    # Define colors and risk levels based on safety score
    def get_color(score):
        if score >= 70: return [5, 150, 105]   # Green (Safe)
        if score >= 40: return [217, 119, 6]  # Amber (Moderate)
        return [220, 38, 38]                   # Red (High Risk)
        
    def get_risk(score):
        if score >= 70: return "Low Risk"
        if score >= 40: return "Moderate"
        return "High Risk"

    vehicle_stats["color"] = vehicle_stats["safety_score"].apply(get_color)
    vehicle_stats["risk_level"] = vehicle_stats["safety_score"].apply(get_risk)
    vehicle_stats["alert_count"] = vehicle_stats["aggressive"]  # Using aggressive trips as a proxy for alerts
    vehicle_stats["radius"] = 250 + (100 - vehicle_stats["safety_score"]) * 5  # Higher risk = bigger dot
    
    # Format safety score for tooltip
    vehicle_stats["safety_score"] = vehicle_stats["safety_score"].round(1)

    st.markdown("""
    <div class="content-card">
      <div class="content-card-title">Live Fleet Positions</div>
      <div class="content-card-tag">Simulated GPS Data</div>
    </div>
    """, unsafe_allow_html=True)
    
    render_fleet_map(vehicle_stats, lat_col="lat", lon_col="lon", color_col="color")
    
    # Legend
    st.markdown("""
    <div style="display:flex; justify-content:center; gap:20px; font-family:'DM Sans', sans-serif; font-size:12px; margin-top:10px;">
        <div style="display:flex; align-items:center; gap:5px;"><span style="display:inline-block; width:12px; height:12px; background-color:#059669; border-radius:50%;"></span> Safe (≥70)</div>
        <div style="display:flex; align-items:center; gap:5px;"><span style="display:inline-block; width:12px; height:12px; background-color:#d97706; border-radius:50%;"></span> Moderate (40-69)</div>
        <div style="display:flex; align-items:center; gap:5px;"><span style="display:inline-block; width:12px; height:12px; background-color:#dc2626; border-radius:50%;"></span> High Risk (<40)</div>
    </div>
    """, unsafe_allow_html=True)

page_footer()
