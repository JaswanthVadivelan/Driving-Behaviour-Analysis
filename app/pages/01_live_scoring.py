import bootstrap

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.config.theme import AXIS, PLOTLY_BASE, apply_theme, page_footer, render_nav, render_topbar
from core.alerts.alert_engine import AlertEngine
from core.scoring.scorer import TripScorer
from core.utils.history_manager import HistoryManager


st.set_page_config(
    page_title="Live Scoring | DBAS",
    layout="wide",
    page_icon="DBAS",
    initial_sidebar_state="collapsed",
)

apply_theme()
render_topbar()
render_nav("Live Scoring")

st.markdown(
    """
<style>
.block-container {
  padding-top: 1rem !important;
  padding-bottom: 2rem !important;
  max-width: 1280px !important;
}

.live-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  padding: 18px 0 22px;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.live-hero h1 {
  margin: 0;
  font-family: var(--font-d);
  font-size: 40px;
  line-height: 1.05;
  letter-spacing: -0.04em;
  color: var(--text);
}

.live-hero p {
  margin: 10px 0 0;
  max-width: 760px;
  font-family: var(--font-b);
  font-size: 15px;
  color: var(--text-2);
}

.live-pill {
  align-self: center;
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid rgba(37, 99, 235, 0.12);
  background: rgba(37, 99, 235, 0.08);
  color: var(--blue);
  font-family: var(--font-m);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.live-section {
  margin: 22px 0 12px;
  font-family: var(--font-m);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted);
}

.panel-title {
  font-family: var(--font-d);
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text);
  margin-bottom: 6px;
}

.panel-subtitle {
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.6;
}

.panel-tag {
  font-family: var(--font-m);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--blue);
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.14);
  border-radius: 999px;
  padding: 6px 12px;
  display: inline-block;
}

[data-testid="stTextInput"] input,
[data-testid="stFileUploader"] section,
[data-testid="stCheckbox"] label {
  border-radius: 14px !important;
}

[data-testid="stTextInput"] input {
  background: rgba(255, 255, 255, 0.92) !important;
  border: 1px solid rgba(148, 163, 184, 0.22) !important;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04) !important;
}

[data-testid="stButton"] > button[kind="primary"] {
  background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
  border: none !important;
  color: #ffffff !important;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.18) !important;
}

[data-testid="stDataFrame"] > div {
  border: 1px solid rgba(148, 163, 184, 0.16) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04) !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def list_csv_sources(project_root: Path) -> list[Path]:
    sources = [
        *sorted((project_root / "datasets").glob("*.csv"), key=lambda p: p.name.lower()),
        *sorted((project_root / "data" / "raw").glob("*.csv"), key=lambda p: p.name.lower()),
    ]
    return sources


def build_option_labels(paths: list[Path]) -> tuple[list[str], dict[str, Path], str]:
    placeholder = "Select a CSV from datasets/ or data/raw"
    if not paths:
        return [placeholder], {}, placeholder

    names = [p.name for p in paths]
    has_duplicates = len(set(names)) != len(names)
    labels = []
    label_to_path: dict[str, Path] = {}

    for path in paths:
        label = f"{path.parent.name}/{path.name}" if has_duplicates else path.name
        labels.append(label)
        label_to_path[label] = path

    return [placeholder] + labels, label_to_path, placeholder


def load_csv_from_source(source) -> pd.DataFrame:
    if hasattr(source, "getvalue") or hasattr(source, "read"):
        return pd.read_csv(source)
    return pd.read_csv(Path(source))


def render_preview(df: pd.DataFrame, source_label: str) -> None:
    with st.container(border=True):
        head_left, head_right = st.columns([3, 1], gap="small")
        with head_left:
            st.markdown('<div class="panel-title">Loaded Preview</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="panel-subtitle">Quick look at the active CSV before scoring.</div>',
                unsafe_allow_html=True,
            )
        with head_right:
            st.markdown(f'<div style="text-align:right;"><span class="panel-tag">{Path(source_label).name}</span></div>', unsafe_allow_html=True)

        stat_left, stat_mid, stat_right = st.columns(3, gap="small")
        with stat_left:
            st.metric("Rows", len(df))
        with stat_mid:
            st.metric("Columns", len(df.columns))
        with stat_right:
            st.metric("Source", Path(source_label).name)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
        st.caption(f"Path: `{source_label}`")


def score_trips(input_df: pd.DataFrame, vehicle_id: str) -> tuple[pd.DataFrame, list]:
    speed_cols = [f"speed_t{i}" for i in range(50)]
    missing_cols = [c for c in speed_cols if c not in input_df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.caption("Expected columns: speed_t0 through speed_t49")
        st.stop()

    with st.spinner("Analysing driving behaviour..."):
        scorer = TripScorer()
        scored_df = scorer.score_dataframe(input_df)

    if "trip_id" not in scored_df.columns:
        scored_df["trip_id"] = [f"trip_{i}" for i in range(len(scored_df))]

    history = HistoryManager()
    alert_engine = AlertEngine()

    alerts = alert_engine.generate_batch_alerts(scored_df, vehicle_id)
    history.save_trips(scored_df, vehicle_id)
    if alerts:
        alert_engine.save_alerts(alerts)

    return scored_df, alerts


def render_results(scored_df: pd.DataFrame, alerts: list) -> None:
    st.markdown('<div class="live-section">Scoring Results</div>', unsafe_allow_html=True)

    total_trips = len(scored_df)
    calm_trips = int((scored_df["label"] == "calm").sum())
    aggressive_trips = int((scored_df["label"] == "aggressive").sum())
    avg_score = float(scored_df["safety_score"].mean())

    m1, m2, m3, m4 = st.columns(4, gap="small")
    with m1:
        st.metric("Total Trips", total_trips)
    with m2:
        st.metric("Calm Trips", calm_trips)
    with m3:
        st.metric("Aggressive Trips", aggressive_trips)
    with m4:
        st.metric("Avg Safety Score", f"{avg_score:.1f}")

    st.markdown('<div class="live-section">Trip Analytics</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns(2, gap="small")

    with chart_left:
        bar_colors = ["#059669" if label == "calm" else "#dc2626" for label in scored_df["label"]]
        fig_bar = go.Figure(
            go.Bar(
                x=scored_df["trip_id"],
                y=scored_df["safety_score"],
                marker=dict(color=bar_colors, line=dict(width=0)),
                hovertemplate="<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>",
            )
        )
        fig_bar.update_layout(
            **PLOTLY_BASE,
            height=280,
            margin=dict(l=8, r=8, t=8, b=8),
            xaxis=dict(title="Trip ID", **AXIS),
            yaxis=dict(title="Safety Score", range=[0, 105], **AXIS),
            bargap=0.3,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_right:
        counts = scored_df["label"].value_counts().reset_index()
        counts.columns = ["label", "count"]
        fig_pie = go.Figure(
            go.Pie(
                labels=counts["label"],
                values=counts["count"],
                hole=0.68,
                marker=dict(
                    colors=["#059669" if label == "calm" else "#dc2626" for label in counts["label"]],
                    line=dict(color="#ffffff", width=3),
                ),
                hovertemplate="<b>%{label}</b><br>%{value} trips<extra></extra>",
            )
        )
        fig_pie.update_layout(
            **PLOTLY_BASE,
            height=280,
            margin=dict(l=8, r=8, t=8, b=8),
            showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div class="live-section">Detailed Results</div>', unsafe_allow_html=True)
    st.dataframe(
        scored_df[["trip_id", "label", "confidence", "safety_score"]].copy(),
        use_container_width=True,
        hide_index=True,
        column_config={
            "trip_id": st.column_config.TextColumn("Trip ID"),
            "label": st.column_config.TextColumn("Label"),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.3f"),
            "safety_score": st.column_config.NumberColumn("Safety Score", format="%.1f"),
        },
    )

    if alerts:
        st.markdown('<div class="live-section">Triggered Alerts</div>', unsafe_allow_html=True)
        for alert in alerts:
            st.warning(f"{alert['alert_type']}: {alert['message']}")

    st.markdown('<div class="live-section">Export</div>', unsafe_allow_html=True)
    st.download_button(
        "Download scored CSV",
        data=scored_df.to_csv(index=False).encode("utf-8"),
        file_name="scored_trips.csv",
        mime="text/csv",
        type="primary",
    )


project_root = Path(__file__).resolve().parents[2]
datasets_dir = project_root / "datasets"
raw_dir = project_root / "data" / "raw"
datasets_dir.mkdir(parents=True, exist_ok=True)
raw_dir.mkdir(parents=True, exist_ok=True)

st.markdown(
    """
<div class="live-hero">
  <div>
    <h1>Live Trip Scorer</h1>
    <p>Choose a CSV, preview it instantly, and score trips when you are ready. The page stays light and the selected file is always visible in the dropdown.</p>
  </div>
  <div class="live-pill">DTW + SVM</div>
</div>
""",
    unsafe_allow_html=True,
)

csv_paths = list_csv_sources(project_root)
dataset_options, path_by_label, dataset_placeholder = build_option_labels(csv_paths)

with st.container(border=True):
    header_left, header_right = st.columns([3, 1], gap="small")
    with header_left:
        st.markdown('<div class="panel-title">Trip Input</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-subtitle">Pick a stored dataset or upload a new CSV, then review the preview before scoring.</div>',
            unsafe_allow_html=True,
        )
    with header_right:
        st.markdown(f'<div style="text-align:right;"><span class="panel-tag">{len(csv_paths)} CSV files</span></div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2], gap="small")
    with left_col:
        vehicle_id = st.text_input("Vehicle ID", placeholder="e.g. TN 14 AK 3524")
    with right_col:
        selected_dataset = st.selectbox(
            "Select dataset from folder",
            options=dataset_options,
            index=0,
            key="live_scoring_dataset_select",
            help="Select a CSV from datasets/ or data/raw",
        )

    upload_col, toggle_col = st.columns([3, 1], gap="small")
    with upload_col:
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    with toggle_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        save_upload = st.checkbox("Save upload")

    st.caption("Required columns: speed_t0 to speed_t49")

input_df = None
source_label = None

if selected_dataset != dataset_placeholder:
    selected_path = path_by_label.get(selected_dataset)
    if selected_path is None:
        st.error(f"Selected file is not available: {selected_dataset}")
        st.stop()
    if not selected_path.exists():
        st.error(f"CSV not found: {selected_path}")
        st.stop()
    try:
        input_df = load_csv_from_source(selected_path)
        source_label = str(selected_path)
    except Exception as exc:
        st.error(f"Failed to load CSV: {exc}")
        st.stop()
elif uploaded_file is not None:
    try:
        input_df = load_csv_from_source(uploaded_file)
        source_label = uploaded_file.name
    except Exception as exc:
        st.error(f"Failed to load uploaded CSV: {exc}")
        st.stop()

if input_df is not None:
    st.markdown('<div class="live-section">Loaded Preview</div>', unsafe_allow_html=True)
    render_preview(input_df, source_label or "Unknown")

if st.button("Score Trips", type="primary"):
    if not vehicle_id:
        st.error("Please enter a Vehicle ID before scoring.")
    elif input_df is None:
        st.error("Please upload a CSV or select one from the folder.")
    else:
        if uploaded_file is not None and selected_dataset == dataset_placeholder and save_upload:
            upload_path = datasets_dir / uploaded_file.name
            with open(upload_path, "wb") as handle:
                handle.write(uploaded_file.getbuffer())

        scored_df, alerts = score_trips(input_df, vehicle_id)
        render_results(scored_df, alerts)

page_footer()
