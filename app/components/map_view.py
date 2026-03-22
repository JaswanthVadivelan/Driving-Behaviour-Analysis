# components/map_view.py
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

def render_fleet_map(df, lat_col="lat", lon_col="lon", color_col="color"):
    """Render a professional PyDeck fleet map with tooltips and zoom."""
    if df.empty:
        st.info("No spatial data available for map visualization.")
        return

    # Create PyDeck layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=[lon_col, lat_col],
        get_color=color_col,
        get_radius="radius",
        pickable=True,
        opacity=0.8,
        filled=True,
        stroked=True,
        line_width_min_pixels=1,
        get_line_color=[255, 255, 255]
    )
    
    # Calculate bounds for initial view
    lat_center = df[lat_col].mean()
    lon_center = df[lon_col].mean()

    # Determine map style based on selected theme
    theme = st.session_state.get("theme", "Light")
    map_style = pdk.map_styles.LIGHT if theme == "Light" else "mapbox://styles/mapbox/dark-v11"
    
    if theme == "Dark":
        map_style = pdk.map_styles.DARK

    view_state = pdk.ViewState(
        latitude=lat_center,
        longitude=lon_center,
        zoom=10,
        pitch=0,
    )

    tooltip = {
        "html": "<b>Vehicle ID:</b> {vehicle_id} <br/>"
                "<b>Score:</b> {safety_score} <br/>"
                "<b>Alerts:</b> {alert_count} <br/>"
                "<b>Risk:</b> {risk_level}",
        "style": {
            "backgroundColor": "#ffffff" if theme == "Light" else "#111827",
            "color": "#0f172a" if theme == "Light" else "#f9fafb",
            "fontFamily": "'DM Sans', sans-serif",
            "fontSize": "12px",
            "padding": "10px",
            "borderRadius": "8px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
            "border": "1px solid #e2e8f0"
        }
    }

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=map_style,
        tooltip=tooltip
    )
    
    st.pydeck_chart(deck)
