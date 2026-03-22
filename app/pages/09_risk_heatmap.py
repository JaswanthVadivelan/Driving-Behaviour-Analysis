import bootstrap
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from core.utils.history_manager import HistoryManager
from app.config.theme import apply_theme, render_topbar, render_nav, render_page_header, page_footer, get_plotly_layout, get_axis_layout
from app.components.chart_card import render_chart_card

st.set_page_config(page_title="Risk Heatmap", layout="wide", page_icon="🔥", initial_sidebar_state="collapsed")
apply_theme()
render_topbar()
render_nav("Risk Heatmap")
render_page_header("Risk Heatmap", "Temporal and contextual risk analysis", badge="v1.0 · Insights")

history_manager = HistoryManager()
history_df = history_manager.load_history()

if history_df.empty:
    st.info("No trip history available.")
else:
    history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
    history_df["hour"] = history_df["timestamp"].dt.hour
    history_df["day_of_week"] = history_df["timestamp"].dt.day_name()
    history_df["time_of_day"] = history_df["hour"].apply(lambda x: "Night" if x < 6 or x >= 18 else "Day")
    
    plotly_layout = get_plotly_layout()
    axis_layout = get_axis_layout()

    # Layout Row 1
    c1, c2 = st.columns(2)
    
    with c1:
        # Day vs Night
        d_vs_n = history_df.groupby(["time_of_day", "label"]).size().unstack(fill_value=0).reset_index()
        fig1 = go.Figure()
        if "calm" in d_vs_n.columns:
            fig1.add_trace(go.Bar(x=d_vs_n["time_of_day"], y=d_vs_n["calm"], name="Calm", marker_color="#059669"))
        if "aggressive" in d_vs_n.columns:
            fig1.add_trace(go.Bar(x=d_vs_n["time_of_day"], y=d_vs_n["aggressive"], name="Aggressive", marker_color="#dc2626"))
        
        fig1.update_layout(
            barmode="stack",
            xaxis=dict(title="Time of Day", **axis_layout),
            yaxis=dict(title="Trips", **axis_layout),
            **plotly_layout,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        render_chart_card("Day vs Night Driving", "Trip Classification", fig1)

    with c2:
        # Histogram of safety scores
        fig2 = px.histogram(history_df, x="safety_score", nbins=20, color="label", 
                            color_discrete_map={"calm": "#059669", "aggressive": "#dc2626"},
                            opacity=0.8, marginal="box")
        fig2.update_layout(
            xaxis=dict(title="Safety Score", **axis_layout),
            yaxis=dict(title="Count", **axis_layout),
            **plotly_layout,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        render_chart_card("Safety Score Distribution", "Histogram", fig2)

    # Risk Heatmap (Day of Week vs Hour)
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    
    # Calculate aggressive % per hour and day
    heatmap_data = history_df.groupby(["day_of_week", "hour"]).apply(
        lambda x: (x["label"] == "aggressive").sum() / len(x) * 100
    ).reset_index(name="risk_pct")
    
    # Pivot for heatmap
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_pivot = heatmap_data.pivot(index="day_of_week", columns="hour", values="risk_pct").reindex(days_order)
    
    fig3 = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale=[[0, "#059669"], [0.5, "#d97706"], [1, "#dc2626"]],
        hoverongaps=False,
        hovertemplate="Day: %{y}<br>Hour: %{x}:00<br>Aggressive Risk: %{z:.1f}%<extra></extra>"
    ))
    fig3.update_layout(
        xaxis=dict(title="Hour of Day", dtick=1, **axis_layout),
        yaxis=dict(title="Day of Week", **axis_layout),
        **plotly_layout,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    render_chart_card("Aggressive Driving Risk Pattern", "Hourly Heatmap", fig3, height=350)

page_footer()





