# src/report_generator.py
# This module generates PDF reports using ReportLab.

# Import os for filesystem paths.
import os

# Import datetime for timestamping reports.
from datetime import datetime

# Import pandas for data handling.
import pandas as pd

# Import matplotlib for creating charts.
import matplotlib.pyplot as plt

# Import ReportLab units and colors.
from reportlab.lib import colors

# Import ReportLab page size utilities.
from reportlab.lib.pagesizes import letter

# Import ReportLab styles for text formatting.
from reportlab.lib.styles import getSampleStyleSheet

# Import ReportLab flowables for building PDFs.
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

# Import Config for configuration access.
from core.utils.config import Config

# Define a ReportGenerator class to build PDF reports.
class ReportGenerator:
    # Initialize the generator with configuration.
    def __init__(self):
        # Load configuration from YAML.
        self.cfg = Config.load()
        # Ensure the reports directory exists.
        os.makedirs(self.cfg.REPORTS_PATH, exist_ok=True)

    # Generate a PDF report for a single vehicle's trips.
    def generate_trip_report(self, vehicle_id, scored_df):
        # Build a timestamp string for the filename.
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        # Build the output PDF path.
        out_path = os.path.join(self.cfg.REPORTS_PATH, f"{vehicle_id}_{ts}.pdf")
        # Create the PDF document template.
        doc = SimpleDocTemplate(out_path, pagesize=letter)
        # Load a basic stylesheet for paragraphs.
        styles = getSampleStyleSheet()
        # Initialize a list of flowables to build the PDF.
        story = []
        # Add the title as a Paragraph flowable.
        story.append(Paragraph("Driving Behaviour Report", styles["Title"]))
        # Add a spacer for visual separation.
        story.append(Spacer(1, 12))
        # Add vehicle ID and date as a paragraph.
        story.append(Paragraph(f"Vehicle ID: {vehicle_id} | Date: {datetime.utcnow().date()}", styles["Normal"]))
        # Add another spacer.
        story.append(Spacer(1, 12))
        # Compute summary stats for the table.
        total_trips = len(scored_df)
        # Compute percent aggressive.
        pct_aggressive = (scored_df["label"] == "aggressive").mean() * 100.0 if total_trips > 0 else 0.0
        # Compute average safety score.
        avg_safety = float(scored_df["safety_score"].mean()) if total_trips > 0 else 0.0
        # Build the summary table data.
        table_data = [
            ["Total Trips", "% Aggressive", "Avg Safety Score"],
            [str(total_trips), f"{pct_aggressive:.1f}%", f"{avg_safety:.1f}"],
        ]
        # Create a ReportLab Table flowable.
        table = Table(table_data)
        # Apply styling to the table.
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        # Add the table to the story.
        story.append(table)
        # Add a spacer after the table.
        story.append(Spacer(1, 12))
        # Create a bar chart of safety scores per trip.
        fig, ax = plt.subplots(figsize=(6, 3))
        # Plot the safety scores.
        ax.bar(range(len(scored_df)), scored_df["safety_score"], color="steelblue")
        # Label the chart axes.
        ax.set_xlabel("Trip Index")
        ax.set_ylabel("Safety Score")
        # Add a chart title.
        ax.set_title("Safety Scores per Trip")
        # Save the chart as a temporary image.
        temp_img = os.path.join(self.cfg.REPORTS_PATH, f"{vehicle_id}_{ts}_temp.png")
        # Write the figure to disk.
        fig.savefig(temp_img, dpi=150, bbox_inches="tight")
        # Close the figure to free memory.
        plt.close(fig)
        # Add the chart image as a flowable.
        story.append(Image(temp_img, width=400, height=200))
        # Add a spacer after the chart.
        story.append(Spacer(1, 12))
        # Create a risk level summary paragraph.
        if avg_safety < 40:
            risk_text = "Overall risk level: High. Immediate attention recommended."
        elif avg_safety < 70:
            risk_text = "Overall risk level: Medium. Monitor driving patterns closely."
        else:
            risk_text = "Overall risk level: Low. Driving behavior appears safe."
        # Add the risk summary paragraph.
        story.append(Paragraph(risk_text, styles["Normal"]))
        # Build the PDF document with all flowables.
        doc.build(story)
        # Remove the temporary image after embedding.
        if os.path.exists(temp_img):
            os.remove(temp_img)
        # Return the path to the generated report.
        return out_path

    # Generate a fleet-wide PDF report comparing vehicles.
    def generate_fleet_report(self, comparison_df):
        # Build a timestamp string for the filename.
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        # Build the output PDF path.
        out_path = os.path.join(self.cfg.REPORTS_PATH, f"fleet_report_{ts}.pdf")
        # Create the PDF document template.
        doc = SimpleDocTemplate(out_path, pagesize=letter)
        # Load a basic stylesheet for paragraphs.
        styles = getSampleStyleSheet()
        # Initialize a list of flowables to build the PDF.
        story = []

        title_style = styles["Title"]
        title_style.alignment = 1
        story.append(Paragraph("Fleet Intelligence Report", title_style))
        story.append(Spacer(1, 12))

        # Add Insights and Charts
        try:
            from core.utils.history_manager import HistoryManager
            from core.alerts.alert_engine import AlertEngine
            hm = HistoryManager()
            history_df = hm.load_history()
            if not history_df.empty:
                story.append(Paragraph("Fleet AI Insights", styles["Heading2"]))
                
                # Insight 1: Highest risk vehicle
                risk_veh = history_df[history_df["label"] == "aggressive"].groupby("vehicle_id").size().sort_values(ascending=False)
                if not risk_veh.empty:
                    worst_v = risk_veh.index[0]
                    v_trips = history_df[history_df["vehicle_id"]==worst_v]
                    v_pct = (risk_veh.iloc[0] / len(v_trips)) * 100
                    if v_pct > 20:
                        story.append(Paragraph(f"• Vehicle {worst_v} shows {v_pct:.0f}% aggressive trips.", styles["Normal"]))
                
                # Insight 2: Recent Trend
                history_timestamps = pd.to_datetime(history_df["timestamp"], errors="coerce").dt.tz_localize(None)
                last_week = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=7)
                
                df_recent = history_df[history_timestamps >= last_week]
                df_older = history_df[history_timestamps < last_week]
                
                if len(df_recent) > 10 and len(df_older) > 10:
                    recent_risk = (df_recent["label"] == "aggressive").mean() * 100
                    older_risk = (df_older["label"] == "aggressive").mean() * 100
                    delta = recent_risk - older_risk
                    if delta > 5:
                        story.append(Paragraph(f"• Fleet risk increased by {delta:.1f}% this week.", styles["Normal"]))
                    elif delta < -5:
                        story.append(Paragraph(f"• Fleet safety improved. Aggressive driving dropped by {abs(delta):.1f}% this week.", styles["Normal"]))
                
                # Add Alert Summary
                ae = AlertEngine()
                alerts_df = ae.get_all_alerts()
                if not alerts_df.empty:
                    act = len(alerts_df[alerts_df["status"]=="Active"]) if "status" in alerts_df.columns else 0
                    story.append(Paragraph(f"• Active Alerts needing attention: {act}", styles["Normal"]))

                story.append(Spacer(1, 12))
                
                # Chart: Fleet safety by vehicle
                safe_veh = history_df.groupby("vehicle_id")["safety_score"].mean().sort_values()
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.bar(safe_veh.index[:10].astype(str), safe_veh.values[:10], color="#1a56db")
                ax.set_xlabel("Vehicle ID")
                ax.set_ylabel("Avg Safety Score")
                ax.set_title("Fleet Vehicle Scorer")
                temp_img = os.path.join(self.cfg.REPORTS_PATH, f"fleet_chart_{ts}_temp.png")
                fig.savefig(temp_img, dpi=150, bbox_inches="tight")
                plt.close(fig)
                story.append(Image(temp_img, width=400, height=200))
                story.append(Spacer(1, 12))
                
        except Exception as e:
            pass

        story.append(Paragraph("Vehicle Rankings Table", styles["Heading2"]))
        story.append(Spacer(1, 12))

        # Build table data with headers and rows.
        if comparison_df is None or comparison_df.empty:
            story.append(Paragraph("No vehicle data available", styles["Normal"]))
            doc.build(story)
            return out_path

        df = comparison_df.copy()

        # Format columns for readability.
        def _fmt(val):
            if isinstance(val, float):
                return f"{val:.2f}"
            return str(val)

        if "risk_trend" in df.columns:
            def _format_trend(x):
                s = str(x)
                if len(s) > 60:
                    s = s[:57] + "..."
                return s
            df["risk_trend"] = df["risk_trend"].apply(_format_trend)

        df = df.map(_fmt)

        table_data = [df.columns.tolist()] + df.values.tolist()

        # Column widths (fit to letter width ~ 540 pts usable).
        col_widths = [60, 70, 90, 170, 55, 55, 40]
        if len(table_data[0]) != len(col_widths):
            col_widths = None

        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        story.append(table)
        doc.build(story)
        
        # Cleanup
        temp_img_file = os.path.join(self.cfg.REPORTS_PATH, f"fleet_chart_{ts}_temp.png")
        if os.path.exists(temp_img_file):
            os.remove(temp_img_file)
            
        return out_path


    # Generate an alert PDF report for a vehicle or the full fleet.
    def generate_alert_report(self, alerts_df, vehicle_id=None):
        # Build a timestamp string for the filename.
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        # Choose report name based on scope.
        scope = vehicle_id if vehicle_id else "fleet"
        # Build the output PDF path.
        out_path = os.path.join(self.cfg.REPORTS_PATH, f"alert_report_{scope}_{ts}.pdf")
        # Create the PDF document template.
        doc = SimpleDocTemplate(out_path, pagesize=letter)
        # Load a basic stylesheet for paragraphs.
        styles = getSampleStyleSheet()
        # Initialize a list of flowables to build the PDF.
        story = []
        # Add the title as a Paragraph flowable.
        title = "Alert Report" if vehicle_id else "Fleet Alert Report"
        story.append(Paragraph(title, styles["Title"]))
        # Add scope line.
        scope_line = f"Vehicle ID: {vehicle_id}" if vehicle_id else "Scope: All Vehicles"
        story.append(Paragraph(f"{scope_line} | Date: {datetime.utcnow().date()}", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Defensive copy and optional filter.
        df = alerts_df.copy() if alerts_df is not None else pd.DataFrame()
        if vehicle_id and not df.empty and "vehicle_id" in df.columns:
            df = df[df["vehicle_id"] == vehicle_id]

        # If empty after filtering, create a minimal report.
        if df.empty:
            story.append(Paragraph("No alerts available for the selected scope.", styles["Normal"]))
            doc.build(story)
            return out_path

        # Summary metrics.
        total_alerts = len(df)
        unique_vehicles = df["vehicle_id"].nunique() if "vehicle_id" in df.columns else 0
        story.append(Paragraph(f"Total Alerts: {total_alerts}", styles["Normal"]))
        if not vehicle_id:
            story.append(Paragraph(f"Vehicles Affected: {unique_vehicles}", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Alert type breakdown table.
        if "alert_type" in df.columns:
            type_counts = df["alert_type"].value_counts().reset_index()
            type_counts.columns = ["Alert Type", "Count"]
            table_data = [type_counts.columns.tolist()] + type_counts.astype(str).values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            story.append(Paragraph("Alert Type Summary", styles["Heading2"]))
            story.append(table)
            story.append(Spacer(1, 12))

            # Bar chart of alert types.
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.bar(type_counts["Alert Type"], type_counts["Count"], color="#ef4444")
            ax.set_ylabel("Count")
            ax.set_title("Alerts by Type")
            ax.tick_params(axis="x", rotation=30)
            temp_img = os.path.join(self.cfg.REPORTS_PATH, f"alerts_{scope}_{ts}_temp.png")
            fig.savefig(temp_img, dpi=150, bbox_inches="tight")
            plt.close(fig)
            story.append(Image(temp_img, width=400, height=200))
            story.append(Spacer(1, 12))

        # Recent alerts table (limited).
        cols = [c for c in ["timestamp", "vehicle_id", "alert_type", "message"] if c in df.columns]
        if cols:
            recent = df.copy()
            if "timestamp" in recent.columns:
                recent["timestamp"] = pd.to_datetime(recent["timestamp"], errors="coerce")
                recent = recent.sort_values("timestamp", ascending=False)
            recent = recent.head(12)
            table_data = [cols] + recent[cols].astype(str).values.tolist()
            table = Table(table_data, colWidths=[140, 80, 120, 180][: len(cols)])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(Paragraph("Recent Alerts (latest 12)", styles["Heading2"]))
            story.append(table)

        # Build the PDF document with all flowables.
        doc.build(story)

        # Remove temporary image if created.
        try:
            if "temp_img" in locals() and os.path.exists(temp_img):
                os.remove(temp_img)
        except Exception:
            pass

        # Return the path to the generated report.
        return out_path
