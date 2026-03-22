# components/leaderboard_table.py
import streamlit as st
import pandas as pd

def render_leaderboard(df):
    """Render a styled dataframe for the driver leaderboard."""
    if df.empty:
         st.info("No drivers available for ranking.")
         return

    st.dataframe(
        df,
        column_config={
            "Rank": st.column_config.NumberColumn(
                "Rank", help="Current rank based on safety score", format="🏆 %d"
            ),
            "vehicle_id": st.column_config.TextColumn(
                "Vehicle ID", help="Fleet Vehicle Identifier"
            ),
            "safety_score": st.column_config.ProgressColumn(
                "Safety Score", help="Driver's average safety score", min_value=0, max_value=100
            ),
            "trip_count": st.column_config.NumberColumn(
                "Trips", help="Total trips taken"
            ),
            "pct_aggressive": st.column_config.NumberColumn(
                "Aggressive %", help="Percentage of aggressive trips", format="%.1f%%"
            ),
        },
        use_container_width=True,
        hide_index=True
    )

def render_podium(top_drivers):
    """Render podium UI for top 3 drivers."""
    if len(top_drivers) < 3:
        return

    # Extract top 3
    first = top_drivers.iloc[0]
    second = top_drivers.iloc[1]
    third = top_drivers.iloc[2]
    
    col1, col2, col3 = st.columns(3)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; margin-top: 20px;">
          <h2 style="margin:0; font-size:48px;">🏆</h2>
          <div style="background:var(--blue-light); border:1px solid var(--blue); padding:15px; border-radius:12px;">
            <div style="font-weight:700; color:var(--blue); font-size:18px;">1st Place</div>
            <div style="font-weight:bold; font-size:22px; margin:5px 0;">{first['vehicle_id']}</div>
            <div style="color:var(--muted); font-size:14px;">Score: {first['safety_score']:.1f}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col1:
        st.markdown(f"""
        <div style="text-align: center; margin-top: 50px;">
          <h2 style="margin:0; font-size:40px;">🥈</h2>
          <div style="background:var(--surface2); border:1px solid var(--border); padding:15px; border-radius:12px;">
            <div style="font-weight:700; color:var(--text-2); font-size:16px;">2nd Place</div>
            <div style="font-weight:bold; font-size:18px; margin:5px 0;">{second['vehicle_id']}</div>
            <div style="color:var(--muted); font-size:14px;">Score: {second['safety_score']:.1f}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div style="text-align: center; margin-top: 60px;">
          <h2 style="margin:0; font-size:36px;">🥉</h2>
          <div style="background:var(--surface2); border:1px solid var(--border); padding:15px; border-radius:12px;">
            <div style="font-weight:700; color:var(--text-2); font-size:15px;">3rd Place</div>
            <div style="font-weight:bold; font-size:16px; margin:5px 0;">{third['vehicle_id']}</div>
            <div style="color:var(--muted); font-size:14px;">Score: {third['safety_score']:.1f}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
