import bootstrap
import streamlit as st
import pandas as pd

from core.utils.history_manager import HistoryManager
from app.config.theme import apply_theme, render_topbar, render_nav, render_page_header, page_footer
from app.components.leaderboard_table import render_leaderboard, render_podium

st.set_page_config(page_title="Driver Leaderboard", layout="wide", page_icon="🏆", initial_sidebar_state="collapsed")
apply_theme()
render_topbar()
render_nav("Driver Leaderboard")
render_page_header("Driver Leaderboard", "Ranked driver performance across the fleet", badge="v1.0 · Ranking")

history_manager = HistoryManager()
history_df = history_manager.load_history()

if history_df.empty:
    st.info("No trip history available to generate leaderboard.")
else:
    # Summarize history per vehicle
    lb_df = history_df.groupby("vehicle_id").agg(
        trip_count=('trip_id', 'count'),
        safety_score=('safety_score', 'mean'),
        aggressive_count=('label', lambda x: (x == 'aggressive').sum())
    ).reset_index()

    lb_df["pct_aggressive"] = (lb_df["aggressive_count"] / lb_df["trip_count"]) * 100
    
    # Rank: Sort by safety_score descending, then pct_aggressive ascending, then trip_count descending
    lb_df = lb_df.sort_values(by=["safety_score", "pct_aggressive", "trip_count"], ascending=[False, True, False]).reset_index(drop=True)
    lb_df["Rank"] = lb_df.index + 1
    
    st.markdown("""
    <div class="content-card">
      <div class="content-card-title">Top Performers</div>
      <div class="content-card-tag">Podium</div>
    </div>
    """, unsafe_allow_html=True)
    
    render_podium(lb_df)
    
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-card">
      <div class="content-card-title">Full Driver Rankings</div>
      <div class="content-card-tag">Fleet Wide</div>
    </div>
    """, unsafe_allow_html=True)

    # Format dataframe for display
    display_df = lb_df[["Rank", "vehicle_id", "safety_score", "trip_count", "pct_aggressive"]].copy()
    display_df["safety_score"] = display_df["safety_score"].round(1)
    
    render_leaderboard(display_df)

page_footer()





