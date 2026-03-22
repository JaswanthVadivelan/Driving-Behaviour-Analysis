import bootstrap
# pages/5_Reports.py

import os
import importlib
import pandas as pd
import streamlit as st
import core.reports.report_generator as report_generator
report_generator = importlib.reload(report_generator)
ReportGenerator = report_generator.ReportGenerator
from core.profiling.vehicle_profiler import VehicleProfiler
from core.alerts.alert_engine import AlertEngine
from app.config.theme import (
    apply_theme, render_topbar, render_nav,
    render_page_header, section, page_footer,
)

st.set_page_config(
    page_title="Reports — DBAS", layout="wide",
    page_icon="🛡️", initial_sidebar_state="collapsed",
)
apply_theme()
render_topbar()
render_nav("Reports")
render_page_header(
    "Reports",
    "Generate and download PDF safety reports — trip, fleet, and alert summaries",
    badge="PDF Reports",
)

report_gen = ReportGenerator()
profiler   = VehicleProfiler()
alert_eng  = AlertEngine()

# ── Generate Reports ─────────────────────────────────────────────────────────────
section("Generate New Report")

gc1, gc2, gc3 = st.columns(3, gap="small")

# ── Trip Report ──
with gc1:
    st.markdown("""
    <div class="content-card">
      <div class="content-card-title">Trip Report</div>
      <div class="content-card-tag">Per vehicle · PDF</div>
    </div>""", unsafe_allow_html=True)

    vehicle_id = st.text_input("Vehicle ID", placeholder="e.g. TN-14-AK-3524",
                                key="trip_vehicle_id")
    if st.button("📄  Generate Trip Report", type="primary", key="btn_trip"):
        scored_df = profiler.history.load_history(vehicle_id=vehicle_id or None)
        if scored_df is not None and not scored_df.empty and vehicle_id:
            with st.spinner("Generating trip report…"):
                report_path = report_gen.generate_trip_report(vehicle_id, scored_df)
            with open(report_path, "rb") as f:
                pdf_bytes = f.read()
            st.success(f"✓ {os.path.basename(report_path)}")
            st.download_button(
                "⬇  Download Trip Report",
                data=pdf_bytes,
                file_name=os.path.basename(report_path),
                mime="application/pdf",
                key="dl_trip_new",
            )
        else:
            st.error("Enter a valid Vehicle ID that has existing trip history.")

# ── Fleet Report ──
with gc2:
    st.markdown("""
    <div class="content-card">
      <div class="content-card-title">Fleet Report</div>
      <div class="content-card-tag">All vehicles · PDF</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:56px'></div>", unsafe_allow_html=True)
    if st.button("📊  Generate Fleet Report", type="primary", key="btn_fleet"):
        all_ids = profiler.get_all_vehicle_ids()
        comp_df = profiler.compare_vehicles(all_ids)
        with st.spinner("Generating fleet report…"):
            report_path = report_gen.generate_fleet_report(comp_df)
        with open(report_path, "rb") as f:
            pdf_bytes = f.read()
        st.success(f"✓ {os.path.basename(report_path)}")
        st.download_button(
            "⬇  Download Fleet Report",
            data=pdf_bytes,
            file_name=os.path.basename(report_path),
            mime="application/pdf",
            key="dl_fleet_new",
        )

# ── Alert Report ──
with gc3:
    st.markdown("""
    <div class="content-card">
      <div class="content-card-title">Alert Report</div>
      <div class="content-card-tag">Fleet or per vehicle · PDF</div>
    </div>""", unsafe_allow_html=True)

    alert_vehicle_id = st.text_input(
        "Vehicle ID (leave blank for fleet-wide)",
        placeholder="All vehicles if empty",
        key="alert_vehicle_id",
    )
    if st.button("🚨  Generate Alert Report", type="primary", key="btn_alert"):
        try:
            alerts_df = pd.read_csv(alert_eng.alerts_path)
        except Exception:
            alerts_df = pd.DataFrame()

        if alerts_df.empty:
            st.error("No alert data found. Run some trips first to generate alerts.")
        else:
            vid = alert_vehicle_id.strip() or None
            with st.spinner("Generating alert report…"):
                report_path = report_gen.generate_alert_report(alerts_df, vehicle_id=vid)
            with open(report_path, "rb") as f:
                pdf_bytes = f.read()
            st.success(f"✓ {os.path.basename(report_path)}")
            st.download_button(
                "⬇  Download Alert Report",
                data=pdf_bytes,
                file_name=os.path.basename(report_path),
                mime="application/pdf",
                key="dl_alert_new",
            )

# ── Available Reports ─────────────────────────────────────────────────────────────
section("Available Reports")

report_files = sorted(
    [f for f in os.listdir(report_gen.cfg.REPORTS_PATH) if f.lower().endswith(".pdf")],
    reverse=True,
)

if report_files:
    # Type icon + label mapping
    def _report_meta(fname):
        if "fleet" in fname:   return "📊", "Fleet Report",   "rgba(29,111,243,0.1)",  "rgba(29,111,243,0.3)"
        if "trip"  in fname:   return "📄", "Trip Report",    "rgba(0,229,122,0.08)",  "rgba(0,229,122,0.25)"
        if "alert" in fname:   return "🚨", "Alert Report",   "rgba(255,59,92,0.08)",  "rgba(255,59,92,0.25)"
        return "📁", "Report", "rgba(255,255,255,0.05)", "rgba(255,255,255,0.1)"

    cols = st.columns(3, gap="small")
    for i, fname in enumerate(report_files):
        fpath       = os.path.join(report_gen.cfg.REPORTS_PATH, fname)
        fsize       = os.path.getsize(fpath) / 1024
        icon, label, bg, border = _report_meta(fname)

        with open(fpath, "rb") as f:
            data = f.read()

        with cols[i % 3]:
            st.markdown(f"""
            <div class="content-card" style="
                margin-bottom:10px;
                background:{bg};
                border-color:{border};
            ">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:16px;">{icon}</span>
                <span style="font-family:var(--font-m);font-size:9px;letter-spacing:0.1em;
                             text-transform:uppercase;color:var(--muted);">{label}</span>
              </div>
              <div style="font-family:var(--font-b);font-size:12px;font-weight:500;
                          color:var(--text);word-break:break-all;margin-bottom:8px;
                          line-height:1.5;">
                {fname}
              </div>
              <div style="font-family:var(--font-m);font-size:10px;color:var(--dim);">
                {fsize:.1f} KB
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "⬇  Download",
                data=data,
                file_name=fname,
                mime="application/pdf",
                key=f"dl_{fname}",
            )
else:
    st.markdown("""
    <div class="content-card" style="text-align:center;padding:36px 0;">
      <div style="font-family:var(--font-m);font-size:10.5px;letter-spacing:0.12em;
                  text-transform:uppercase;color:var(--dim);">
        No reports generated yet. Use the buttons above to create one.
      </div>
    </div>
    """, unsafe_allow_html=True)

page_footer()





