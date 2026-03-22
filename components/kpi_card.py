# components/kpi_card.py
import streamlit as st

def render_kpi_card(label, value, sub, delta, delta_cls, color, icon="", delay=0):
    """Render a KPI card with animation, soft shadows, hover elevation."""
    # Ensure value handles string and numbers, keeping it professional
    st.markdown(f"""
    <div class="kpi {color}" style="animation-delay:{delay}s">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-val counter-value">{value}</div>
      <div class="kpi-footer">
        <span class="kpi-sub">{sub}</span>
        <span class="kpi-delta {delta_cls}">{delta}</span>
      </div>
    </div>
    <style>
      /* Quick CSS transition added in dbas_theme.py but ensuring it renders smooth */
      .kpi {{ transition: transform 0.3s ease, box-shadow 0.3s ease; }}
      .kpi:hover {{ transform: translateY(-4px); box-shadow: var(--shadow-lg); }}
    </style>
    """, unsafe_allow_html=True)
