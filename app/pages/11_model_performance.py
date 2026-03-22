import bootstrap
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score, confusion_matrix, roc_curve, auc)

from app.config.theme import (
    apply_theme, render_topbar, render_nav,
    render_page_header, section, page_footer,
    get_plotly_layout, get_axis_layout
)
from core.utils.config import Config

st.set_page_config(page_title="Model Performance — DBAS", layout="wide", page_icon="🔬", initial_sidebar_state="collapsed")
apply_theme()
render_topbar()
render_nav("Reports")
render_page_header(
    "Algorithm Performance Analysis",
    "Detailed evaluation of DTW + SVM classification engine against baseline models",
    badge="Benchmark · v1.0"
)

# ── Load & prepare data ──────────────────────────────────────────────────────
@st.cache_data
def load_and_evaluate():
    cfg = Config.load()
    df = pd.read_csv(cfg.FEATURES_PATH)
    speed_cols = [f"speed_t{i}" for i in range(50)]
    if "speed_std" not in df.columns:
        df["speed_std"] = df[speed_cols].std(axis=1)

    y = df["label"].map({"calm": 0, "aggressive": 1}).to_numpy(dtype=int)
    X_raw = df[["jerk", "speed_std"]].to_numpy(dtype=float)
    X_dtw = df[["dtw_calm", "dtw_aggressive"]].to_numpy(dtype=float)

    idx_train, idx_test = train_test_split(
        np.arange(len(df)), test_size=0.2, random_state=42, stratify=y
    )
    Xr_tr, Xr_te = X_raw[idx_train], X_raw[idx_test]
    Xd_tr, Xd_te = X_dtw[idx_train], X_dtw[idx_test]
    y_train, y_test = y[idx_train], y[idx_test]

    models_cfg = {
        "Raw (Jerk+Std) + SVM": (SVC(kernel="rbf", probability=True, random_state=42), Xr_tr, Xr_te),
        "DTW + KNN (k=5)":      (KNeighborsClassifier(n_neighbors=5), Xd_tr, Xd_te),
        "DTW + SVM (RBF) ★":   (SVC(kernel="rbf", probability=True, random_state=42), Xd_tr, Xd_te),
    }

    results = []
    conf_matrices = {}
    roc_data = {}

    for name, (clf, Xtr, Xte) in models_cfg.items():
        clf.fit(Xtr, y_train)
        yp = clf.predict(Xte)
        yp_proba = clf.predict_proba(Xte)[:, 1]
        cv = cross_val_score(clf, Xtr, y_train, cv=StratifiedKFold(n_splits=5), scoring="accuracy")
        fpr, tpr, _ = roc_curve(y_test, yp_proba)
        roc_auc = auc(fpr, tpr)
        results.append({
            "Method": name,
            "Accuracy (%)": round(accuracy_score(y_test, yp) * 100, 2),
            "Precision (%)": round(precision_score(y_test, yp) * 100, 2),
            "Recall (%)": round(recall_score(y_test, yp) * 100, 2),
            "F1-Score (%)": round(f1_score(y_test, yp) * 100, 2),
            "AUC-ROC": round(roc_auc, 4),
            "CV Mean (%)": round(cv.mean() * 100, 2),
            "CV Std (%)": round(cv.std() * 100, 2),
        })
        conf_matrices[name] = confusion_matrix(y_test, yp)
        roc_data[name] = (fpr, tpr, roc_auc)

    return pd.DataFrame(results), conf_matrices, roc_data, int(y_test.sum()), int((y_test==0).sum())

with st.spinner("Running model benchmarks…"):
    results_df, conf_matrices, roc_data, n_agg, n_calm = load_and_evaluate()

best = results_df.loc[results_df["Accuracy (%)"].idxmax()]

# ── Top KPI Cards ────────────────────────────────────────────────────────────
section("Champion Model: DTW + SVM (RBF)")
k1, k2, k3, k4, k5 = st.columns(5, gap="small")
metrics_row = [
    ("Accuracy", f"{best['Accuracy (%)']:.1f}%", "green", "🎯"),
    ("Precision", f"{best['Precision (%)']:.1f}%", "blue", "🔎"),
    ("Recall", f"{best['Recall (%)']:.1f}%", "blue", "📡"),
    ("F1-Score", f"{best['F1-Score (%)']:.1f}%", "green", "⚖️"),
    ("AUC-ROC", f"{best['AUC-ROC']:.4f}", "green", "📈"),
]
for col, (label, val, color, icon) in zip([k1, k2, k3, k4, k5], metrics_row):
    with col:
        st.markdown(f"""
        <div class="kpi {color}">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-val">{val}</div>
            <div class="kpi-footer">
                <span class="kpi-sub">DTW + SVM (RBF)</span>
                <span class="kpi-delta d-up">Best Model</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Dataset Stats ────────────────────────────────────────────────────────────
section("Test Set Composition")
ds1, ds2, ds3 = st.columns(3)
with ds1:
    st.markdown(f"""
    <div class="content-card" style="text-align:center;">
        <div class="content-card-title" style="font-size:32px; color:var(--blue);">{n_calm + n_agg}</div>
        <div class="content-card-tag">Total Test Samples</div>
        <div style="font-size:12px; color:var(--muted); margin-top:8px;">80/20 train-test split — stratified</div>
    </div>
    """, unsafe_allow_html=True)
with ds2:
    st.markdown(f"""
    <div class="content-card" style="text-align:center;">
        <div class="content-card-title" style="font-size:32px; color:var(--green);">{n_calm}</div>
        <div class="content-card-tag">Calm Samples</div>
        <div style="font-size:12px; color:var(--muted); margin-top:8px;">Normal driving behaviour</div>
    </div>
    """, unsafe_allow_html=True)
with ds3:
    st.markdown(f"""
    <div class="content-card" style="text-align:center;">
        <div class="content-card-title" style="font-size:32px; color:var(--red);">{n_agg}</div>
        <div class="content-card-tag">Aggressive Samples</div>
        <div style="font-size:12px; color:var(--muted); margin-top:8px;">Risky driving detected</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
section("Model Comparison Table")
st.dataframe(
    results_df,
    column_config={
        "Method": st.column_config.TextColumn("Model", width="large"),
        "Accuracy (%)": st.column_config.ProgressColumn("Accuracy", min_value=0, max_value=100, format="%.2f%%"),
        "Precision (%)": st.column_config.ProgressColumn("Precision", min_value=0, max_value=100, format="%.2f%%"),
        "Recall (%)": st.column_config.ProgressColumn("Recall", min_value=0, max_value=100, format="%.2f%%"),
        "F1-Score (%)": st.column_config.ProgressColumn("F1-Score", min_value=0, max_value=100, format="%.2f%%"),
        "AUC-ROC": st.column_config.NumberColumn("AUC-ROC", format="%.4f"),
        "CV Mean (%)": st.column_config.NumberColumn("CV Mean", format="%.2f%%"),
        "CV Std (%)": st.column_config.NumberColumn("CV Std", format="±%.2f%%"),
    },
    use_container_width=True,
    hide_index=True,
)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Main Charts Row ──────────────────────────────────────────────────────────
section("Visual Analytics")
ch1, ch2 = st.columns(2, gap="small")

layout = get_plotly_layout()
axis   = get_axis_layout()
COLORS = {"Raw (Jerk+Std) + SVM": "#94a3b8", "DTW + KNN (k=5)": "#f59e0b", "DTW + SVM (RBF) ★": "#1a56db"}

with ch1:
    st.markdown("""<div class="content-card">
      <div class="content-card-title">Accuracy · Precision · Recall · F1</div>
      <div class="content-card-tag">Grouped Bar Chart</div></div>""", unsafe_allow_html=True)

    metrics = ["Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)"]
    fig = go.Figure()
    for _, row in results_df.iterrows():
        fig.add_trace(go.Bar(
            name=row["Method"],
            x=metrics,
            y=[row[m] for m in metrics],
            marker_color=COLORS.get(row["Method"], "#1a56db"),
            text=[f"{row[m]:.1f}%" for m in metrics],
            textposition="outside",
        ))
    fig.update_layout(
        **layout, barmode="group", height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(**axis),
        yaxis=dict(title="Score (%)", range=[0, 115], **axis),
        bargap=0.2, bargroupgap=0.05,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

with ch2:
    st.markdown("""<div class="content-card">
      <div class="content-card-title">ROC Curve — AUC Analysis</div>
      <div class="content-card-tag">True Positive vs False Positive Rate</div></div>""", unsafe_allow_html=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines",
        line=dict(dash="dash", color="#94a3b8", width=1.5),
        name="Random Classifier", showlegend=True
    ))
    for name, (fpr, tpr, roc_auc) in roc_data.items():
        fig2.add_trace(go.Scatter(
            x=fpr, y=tpr, mode="lines", name=f"{name} (AUC={roc_auc:.3f})",
            line=dict(color=COLORS.get(name, "#1a56db"), width=2.5),
        ))
    fig2.update_layout(
        **layout, height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="False Positive Rate", **axis),
        yaxis=dict(title="True Positive Rate", **axis),
        legend=dict(orientation="v", x=0.55, y=0.05),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Confusion Matrices ───────────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
section("Confusion Matrices")
cm_cols = st.columns(3, gap="small")
for col, (name, cm) in zip(cm_cols, conf_matrices.items()):
    with col:
        labels = ["Calm", "Aggressive"]
        fig_cm = go.Figure(go.Heatmap(
            z=cm, x=labels, y=labels,
            text=[[str(v) for v in row] for row in cm],
            texttemplate="%{text}",
            colorscale=[[0, "#eff6ff"], [1, "#1a56db"]],
            showscale=False,
        ))
        fig_cm.update_layout(
            **layout, height=280,
            margin=dict(l=10, r=10, t=50, b=10),
            title=dict(
                text=name, font=dict(size=12, family="'Plus Jakarta Sans', sans-serif"),
                x=0.5
            ),
            xaxis=dict(title="Predicted", **axis),
            yaxis=dict(title="Actual", **axis),
        )
        st.plotly_chart(fig_cm, use_container_width=True)

# ── Algorithm Explanation ────────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
section("How The Algorithm Works")
e1, e2, e3 = st.columns(3, gap="small")
steps = [
    ("1. Speed Profile Input", "🚗", "var(--blue-light)", "var(--blue)",
     "Each trip is represented as a speed time-series: speed_t0 → speed_t49 (50 timesteps sampled at 1-second intervals). This forms the raw temporal driving pattern."),
    ("2. DTW Feature Extraction", "📐", "var(--amber-light)", "var(--amber)",
     "Dynamic Time Warping (DTW) computes how structurally similar the trip's speed curve is to a pre-computed Calm Template and Aggressive Template, captured from training data. This extracts two rich temporal features: dtw_calm and dtw_aggressive."),
    ("3. SVM Classification", "🤖", "var(--green-light)", "var(--green)",
     "The two DTW features feed into a Support Vector Machine (SVM) with a non-linear RBF (Radial Basis Function) kernel. The SVM learned a high-dimensional decision boundary during training to separate Calm from Aggressive driving with maximum margin."),
]
for col, (title, icon, bg, border, desc) in zip([e1, e2, e3], steps):
    with col:
        st.markdown(f"""
        <div style="background:{bg}; border:1px solid {border}20; border-radius:14px; padding:24px; height:100%;">
            <div style="font-size:36px; margin-bottom:12px;">{icon}</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif; font-weight:700; color:{border}; margin-bottom:10px; font-size:14px;">{title}</div>
            <div style="font-family:'DM Sans',sans-serif; font-size:13px; color:var(--text-2); line-height:1.7;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

page_footer()





