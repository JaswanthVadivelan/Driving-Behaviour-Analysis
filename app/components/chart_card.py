# components/chart_card.py
import streamlit as st

def render_chart_card(title, tag, fig=None, height=280):
    """Render a chart content card with optional plotly figure."""
    st.markdown(f"""
    <div class="content-card">
      <div class="content-card-title">{title}</div>
      <div class="content-card-tag">{tag}</div>
    </div>""", unsafe_allow_html=True)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
