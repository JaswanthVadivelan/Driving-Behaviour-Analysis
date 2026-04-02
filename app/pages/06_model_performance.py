import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder

try:
    from core.utils.config import load_config
except Exception:  # pragma: no cover - fallback for legacy config module
    from core.utils.config import Config as _Config

    def load_config():
        return _Config.load()

from app.config.theme import render_topbar, render_nav, render_page_header, page_footer, apply_theme

st.set_page_config(
    page_title="Model Insight & Performance - DBAS",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="collapsed",
)
apply_theme()
render_topbar()
render_nav("Model Performance")
render_page_header(
    title="Model insight & performance",
    subtitle="DTW + SVM — how the model scores driving behaviour",
)


def section_header(label: str):
    st.markdown(f'<div class="dbas-section">{label}</div>', unsafe_allow_html=True)


def apply_plot_style(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#5F5E5A"),
        legend=dict(font=dict(color="#5F5E5A")),
    )
    fig.update_xaxes(tickfont=dict(color="#5F5E5A"), title=dict(font=dict(color="#5F5E5A")))
    fig.update_yaxes(tickfont=dict(color="#5F5E5A"), title=dict(font=dict(color="#5F5E5A")))
    return fig


@st.cache_data(show_spinner=False)
def load_feature_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


config = load_config()
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def resolve_path(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(project_root, path)


features_path = resolve_path(getattr(config, "FEATURES_PATH", "data/processed/trips_features.csv"))
history_path = resolve_path(getattr(config, "HISTORY_PATH", "data/processed/trip_history.csv"))

if not os.path.exists(features_path):
    st.warning(
        "No feature data found. Run pipelines/step3_dtw_features.py and "
        "step4_svm_train.py first."
    )
    st.stop()

feature_df = load_feature_data(features_path)

feature_cols = ["dtw_calm", "dtw_aggressive"]
X = feature_df[feature_cols].values
le = LabelEncoder()
y = le.fit_transform(feature_df["label"])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

section_header("Top KPI metrics")
with st.spinner("Computing model metrics..."):
    try:
        svm_model = SVC(kernel="rbf", probability=True, random_state=42)
        svm_model.fit(X_train, y_train)
        y_pred = svm_model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        precision = precision_score(y_test, y_pred, average="weighted")
        recall = recall_score(y_test, y_pred, average="weighted")

        cv_scores = cross_val_score(
            svm_model, X_train, y_train, cv=5, scoring="f1_weighted"
        )
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
    except Exception as exc:
        st.error(f"SVM training failed: {exc}")
        svm_model = None
        y_pred = np.zeros_like(y_test)
        accuracy = f1 = precision = recall = cv_mean = cv_std = 0.0

k1, k2, k3, k4, k5 = st.columns(5, gap="small")
with k1:
    st.metric("Model accuracy", f"{accuracy:.1%}")
with k2:
    st.metric("F1 score", f"{f1:.3f}")
with k3:
    st.metric("Precision", f"{precision:.3f}")
with k4:
    st.metric("Recall", f"{recall:.3f}")
with k5:
    st.metric("Cross-val F1", f"{cv_mean:.3f} ? {cv_std:.3f}")

st.divider()
section_header("Confusion matrix and feature importance")

c1, c2 = st.columns(2, gap="large")

with c1:
    with st.spinner("Computing model metrics..."):
        try:
            cm = confusion_matrix(y_test, y_pred)
            cm_text = [[str(cell) for cell in row] for row in cm]
            fig_cm = ff.create_annotated_heatmap(
                z=cm.tolist(),
                x=["Predicted calm", "Predicted aggressive"],
                y=["Actual calm", "Actual aggressive"],
                colorscale=[[0, "#EAF3DE"], [0.5, "#9FE1CB"], [1, "#1D9E75"]],
                annotation_text=cm_text,
                showscale=False,
            )
            fig_cm.update_layout(title="Confusion matrix", margin=dict(l=10, r=10, t=40, b=10))
            fig_cm.update_xaxes(title_text="")
            fig_cm.update_yaxes(title_text="")
            apply_plot_style(fig_cm)
            st.plotly_chart(fig_cm, use_container_width=True)
        except Exception as exc:
            st.warning(f"Could not render confusion matrix: {exc}")

with c2:
    with st.spinner("Computing model metrics..."):
        try:
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(X_train, y_train)
            importances = rf_model.feature_importances_
            fi_df = pd.DataFrame(
                {"Feature": feature_cols, "Importance": importances}
            ).sort_values("Importance")
            fig_fi = px.bar(
                fi_df,
                x="Importance",
                y="Feature",
                orientation="h",
                color_discrete_sequence=["#1D9E75"],
                title="Feature importance (Random Forest)",
                labels=dict(x="Importance", y="Feature"),
            )
            fig_fi.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            apply_plot_style(fig_fi)
            st.plotly_chart(fig_fi, use_container_width=True)
        except Exception as exc:
            st.warning(f"Could not render feature importance: {exc}")

st.divider()
section_header("Model comparison")

models_to_compare = {
    "SVM ? RBF (current)": SVC(kernel="rbf", probability=True, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "Naive Bayes": GaussianNB(),
}

rows = []
with st.spinner("Computing model metrics..."):
    for name, model in models_to_compare.items():
        try:
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            rows.append(
                {
                    "Algorithm": name,
                    "Accuracy": accuracy_score(y_test, pred),
                    "F1": f1_score(y_test, pred, average="weighted"),
                    "Precision": precision_score(y_test, pred, average="weighted"),
                    "Recall": recall_score(y_test, pred, average="weighted"),
                    "Status": "Active (selected)" if "SVM" in name else "Compared",
                }
            )
        except Exception as exc:
            st.error(f"{name} failed during training: {exc}")

comparison_df = pd.DataFrame(rows)
if not comparison_df.empty:
    comparison_df.loc[comparison_df["Algorithm"].str.contains("Naive"), "Status"] = "Rejected"
    comparison_df["Accuracy"] = comparison_df["Accuracy"].map(lambda v: f"{v:.1%}")
    comparison_df["F1"] = comparison_df["F1"].map(lambda v: f"{v:.3f}")
    comparison_df["Precision"] = comparison_df["Precision"].map(lambda v: f"{v:.3f}")
    comparison_df["Recall"] = comparison_df["Recall"].map(lambda v: f"{v:.3f}")
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
else:
    st.info("No model comparison results available.")

st.caption(
    "SVM was chosen for its strong weighted F1 score on small feature sets "
    "and robust performance on non-linear boundaries."
)

st.divider()
section_header("DTW feature space")

try:
    hover_cols = [
        col for col in ["vehicle_id", "safety_score"] if col in feature_df.columns
    ]
    fig_scatter = px.scatter(
        feature_df,
        x="dtw_calm",
        y="dtw_aggressive",
        color="label",
        color_discrete_map={"calm": "#1D9E75", "aggressive": "#D85A30"},
        opacity=0.7,
        title="DTW feature space ? calm vs aggressive trips",
        labels={
            "dtw_calm": "DTW distance to calm template",
            "dtw_aggressive": "DTW distance to aggressive template",
        },
        hover_data=hover_cols if hover_cols else None,
    )
    fig_scatter.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    apply_plot_style(fig_scatter)
    st.plotly_chart(fig_scatter, use_container_width=True)
except Exception as exc:
    st.warning(f"Could not render DTW feature scatter plot: {exc}")

st.caption(
    "Each dot is one trip. The SVM finds the optimal boundary separating "
    "the two clusters. Trips closer to the bottom-right are calm; trips closer "
    "to the top-left are aggressive."
)

st.divider()
section_header("Safety score distribution")

if os.path.exists(history_path):
    try:
        history_df = pd.read_csv(history_path)
        fig_hist = px.histogram(
            history_df,
            x="safety_score",
            color="label",
            nbins=20,
            barmode="overlay",
            opacity=0.7,
            color_discrete_map={"calm": "#1D9E75", "aggressive": "#D85A30"},
            title="Safety score distribution across all scored trips",
            labels={
                "safety_score": "Safety score (0?100)",
                "count": "Number of trips",
            },
        )
        fig_hist.add_vline(
            x=40,
            line_dash="dash",
            line_color="#D85A30",
            annotation_text="Alert threshold",
        )
        fig_hist.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        apply_plot_style(fig_hist)
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption("Trips scoring below 40 trigger automatic alerts.")
    except Exception as exc:
        st.warning(f"Could not render safety score distribution: {exc}")
else:
    st.info("Trip history not found. Safety score distribution unavailable.")

st.divider()
section_header("DTW warping path explainer")

try:
    rng = np.random.default_rng(42)
    x_axis = np.arange(50)
    calm_speed = 40 + 20 * np.sin(np.linspace(0, 2 * np.pi, 50))
    aggr_speed = calm_speed.copy()
    spike_idx = rng.choice(np.arange(5, 45), size=6, replace=False)
    aggr_speed[spike_idx] += rng.uniform(10, 25, size=spike_idx.size)
    aggr_speed = np.clip(aggr_speed, 15, 85)

    fig_speed = go.Figure()
    fig_speed.add_trace(
        go.Scatter(
            x=x_axis,
            y=calm_speed,
            mode="lines",
            name="Calm template",
            line=dict(color="#1D9E75", width=3),
        )
    )
    fig_speed.add_trace(
        go.Scatter(
            x=x_axis,
            y=aggr_speed,
            mode="lines",
            name="Aggressive template",
            line=dict(color="#D85A30", width=3),
        )
    )
    fig_speed.update_layout(
        title="Speed profile ? calm vs aggressive template comparison",
        xaxis_title="Time step (0?49)",
        yaxis_title="Speed (km/h)",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    apply_plot_style(fig_speed)
    st.plotly_chart(fig_speed, use_container_width=True)
except Exception as exc:
    st.warning(f"Could not render DTW template comparison: {exc}")

st.caption(
    "The DTW algorithm measures how different a new trip's speed shape is "
    "from each of these templates, even if timings differ."
)

st.divider()
section_header("Cross-validation performance")

cv_models = {
    "SVM": SVC(kernel="rbf", probability=True, random_state=42),
    "RF": RandomForestClassifier(n_estimators=100, random_state=42),
    "GB": GradientBoostingClassifier(random_state=42),
    "NB": GaussianNB(),
}

cv_results = []
with st.spinner("Computing model metrics..."):
    for name, model in cv_models.items():
        try:
            scores = cross_val_score(model, X, y, cv=5, scoring="f1_weighted")
            cv_results.append(
                {
                    "Model": name,
                    "Mean": scores.mean(),
                    "Std": scores.std(),
                }
            )
        except Exception as exc:
            st.error(f"Cross-validation failed for {name}: {exc}")

if cv_results:
    try:
        cv_df = pd.DataFrame(cv_results)
        fig_cv = px.bar(
            cv_df,
            x="Model",
            y="Mean",
            error_y="Std",
            color="Model",
            color_discrete_sequence=["#1D9E75", "#378ADD", "#EF9F27", "#D85A30"],
            title="5-fold cross-validation F1 score by model",
            labels={"Model": "Model", "Mean": "Mean F1 (weighted)"},
        )
        fig_cv.update_layout(margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        fig_cv.add_annotation(
            x="SVM",
            y=cv_df.loc[cv_df["Model"] == "SVM", "Mean"].max(),
            text="Selected model",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-40,
            font=dict(color="#1D9E75"),
        )
        apply_plot_style(fig_cv)
        st.plotly_chart(fig_cv, use_container_width=True)
    except Exception as exc:
        st.warning(f"Could not render cross-validation chart: {exc}")
else:
    st.info("Cross-validation results unavailable.")

page_footer()







