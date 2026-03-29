import re

path = r"d:\Project_Dhanush\Project1\app\pages\03_reports.py"

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

original_chunk = """# ── Generate Reports ─────────────────────────────────────────────────────────────
section("Generate New Report")

gc1, gc2, gc3 = st.columns(3, gap="small")

# ── Trip Report ──
with gc1:
    st.markdown(\"""
    <div class="content-card">
      <div class="content-card-title">Trip Report</div>
      <div class="content-card-tag">Per vehicle · PDF</div>
    </div>\""", unsafe_allow_html=True)

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
    st.markdown(\"""
    <div class="content-card">
      <div class="content-card-title">Fleet Report</div>
      <div class="content-card-tag">All vehicles · PDF</div>
    </div>\""", unsafe_allow_html=True)

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
    st.markdown(\"""
    <div class="content-card">
      <div class="content-card-title">Alert Report</div>
      <div class="content-card-tag">Fleet or per vehicle · PDF</div>
    </div>\""", unsafe_allow_html=True)

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
            )"""

new_chunk = """# ── Generate Reports ─────────────────────────────────────────────────────────────
section("Generate New Report")

gc1, gc2, gc3 = st.columns(3, gap="small")

# ── Trip Report ──
with gc1:
    with st.container(border=True):
        st.markdown(\"""
        <div style="margin-bottom: 20px;">
          <div style="font-family: var(--font-d); font-size: 22px; font-weight: 800; color: var(--text); margin-bottom: 4px;">📄 Trip Report</div>
          <div style="font-family: var(--font-m); font-size: 10px; color: var(--blue); letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700;">Per vehicle · PDF</div>
        </div>\""", unsafe_allow_html=True)

        vehicle_id = st.text_input("Vehicle ID", placeholder="e.g. TN-14-AK-3524", key="trip_vehicle_id")
        
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Generate Trip Report", type="primary", key="btn_trip", use_container_width=True):
            scored_df = profiler.history.load_history(vehicle_id=vehicle_id or None)
            if scored_df is not None and not scored_df.empty and vehicle_id:
                with st.spinner("Generating trip report…"):
                    report_path = report_gen.generate_trip_report(vehicle_id, scored_df)
                with open(report_path, "rb") as f:
                    pdf_bytes = f.read()
                st.success(f"✓ {os.path.basename(report_path)}")
                st.download_button(
                    "⬇  Download Report",
                    data=pdf_bytes,
                    file_name=os.path.basename(report_path),
                    mime="application/pdf",
                    key="dl_trip_new",
                    use_container_width=True
                )
            else:
                st.error("Enter a valid Vehicle ID with history.")

# ── Fleet Report ──
with gc2:
    with st.container(border=True):
        st.markdown(\"""
        <div style="margin-bottom: 20px;">
          <div style="font-family: var(--font-d); font-size: 22px; font-weight: 800; color: var(--text); margin-bottom: 4px;">📊 Fleet Report</div>
          <div style="font-family: var(--font-m); font-size: 10px; color: var(--purple); letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700;">All vehicles · PDF</div>
        </div>\""", unsafe_allow_html=True)

        st.markdown("<div style='height:78px'></div>", unsafe_allow_html=True)
        if st.button("Generate Fleet Report", type="primary", key="btn_fleet", use_container_width=True):
            all_ids = profiler.get_all_vehicle_ids()
            comp_df = profiler.compare_vehicles(all_ids)
            with st.spinner("Generating fleet report…"):
                report_path = report_gen.generate_fleet_report(comp_df)
            with open(report_path, "rb") as f:
                pdf_bytes = f.read()
            st.success(f"✓ {os.path.basename(report_path)}")
            st.download_button(
                "⬇  Download Report",
                data=pdf_bytes,
                file_name=os.path.basename(report_path),
                mime="application/pdf",
                key="dl_fleet_new",
                use_container_width=True
            )

# ── Alert Report ──
with gc3:
    with st.container(border=True):
        st.markdown(\"""
        <div style="margin-bottom: 20px;">
          <div style="font-family: var(--font-d); font-size: 22px; font-weight: 800; color: var(--text); margin-bottom: 4px;">🚨 Alert Report</div>
          <div style="font-family: var(--font-m); font-size: 10px; color: var(--red); letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700;">Fleet or per vehicle · PDF</div>
        </div>\""", unsafe_allow_html=True)

        alert_vehicle_id = st.text_input(
            "Vehicle ID (Optional)",
            placeholder="Blank for fleet-wide",
            key="alert_vehicle_id",
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Generate Alert Report", type="primary", key="btn_alert", use_container_width=True):
            try:
                alerts_df = pd.read_csv(alert_eng.alerts_path)
            except Exception:
                alerts_df = pd.DataFrame()

            if alerts_df.empty:
                st.error("No alerts found.")
            else:
                vid = alert_vehicle_id.strip() or None
                with st.spinner("Generating alert report…"):
                    report_path = report_gen.generate_alert_report(alerts_df, vehicle_id=vid)
                with open(report_path, "rb") as f:
                    pdf_bytes = f.read()
                st.success(f"✓ {os.path.basename(report_path)}")
                st.download_button(
                    "⬇  Download Report",
                    data=pdf_bytes,
                    file_name=os.path.basename(report_path),
                    mime="application/pdf",
                    key="dl_alert_new",
                    use_container_width=True
                )"""

if original_chunk in text:
    text = text.replace(original_chunk, new_chunk)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully replaced layout!")
else:
    print("Could not find the exact chunk in the file.")
