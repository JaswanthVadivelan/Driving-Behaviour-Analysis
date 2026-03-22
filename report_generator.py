# src/report_generator.py
# Generates professional PDF reports for trip and fleet analysis.

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from src.config import Config


# ── Colour palette (matches the dark UI, but PDF uses light background) ──────────
C_DARK      = colors.HexColor("#0b1221")
C_BLUE      = colors.HexColor("#1d6ff3")
C_GREEN     = colors.HexColor("#00c96e")
C_AMBER     = colors.HexColor("#f5a623")
C_RED       = colors.HexColor("#ff3b5c")
C_SURFACE   = colors.HexColor("#f0f4f8")
C_BORDER    = colors.HexColor("#dde3ec")
C_TEXT      = colors.HexColor("#111827")
C_MUTED     = colors.HexColor("#6b7280")
C_WHITE     = colors.white


# ── Style helpers ────────────────────────────────────────────────────────────────
def _styles():
    return {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            textColor=C_WHITE,
            alignment=TA_LEFT,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#93c5fd"),
            alignment=TA_LEFT,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#6b84a8"),
            alignment=TA_LEFT,
        ),
        "section_head": ParagraphStyle(
            "section_head",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=C_MUTED,
            spaceBefore=18,
            spaceAfter=6,
            letterSpacing=1.4,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=C_DARK,
            spaceBefore=14,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=C_TEXT,
            spaceAfter=6,
        ),
        "body_small": ParagraphStyle(
            "body_small",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=C_MUTED,
        ),
        "table_head": ParagraphStyle(
            "table_head",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=C_WHITE,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=C_TEXT,
            alignment=TA_CENTER,
        ),
        "table_cell_left": ParagraphStyle(
            "table_cell_left",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=C_TEXT,
            alignment=TA_LEFT,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=C_MUTED,
            alignment=TA_CENTER,
        ),
        "kpi_value": ParagraphStyle(
            "kpi_value",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=C_DARK,
            alignment=TA_CENTER,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=C_MUTED,
            alignment=TA_CENTER,
            letterSpacing=0.8,
        ),
        "risk_high": ParagraphStyle(
            "risk_high",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=C_RED,
            alignment=TA_CENTER,
        ),
        "risk_med": ParagraphStyle(
            "risk_med",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=C_AMBER,
            alignment=TA_CENTER,
        ),
        "risk_low": ParagraphStyle(
            "risk_low",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=C_GREEN,
            alignment=TA_CENTER,
        ),
    }


def _score_color(score):
    try:
        v = float(score)
    except Exception:
        return C_MUTED
    if v >= 70:
        return C_GREEN
    if v >= 40:
        return C_AMBER
    return C_RED


def _risk_label(score):
    try:
        v = float(score)
    except Exception:
        return "N/A"
    if v >= 70:
        return "LOW"
    if v >= 40:
        return "MODERATE"
    return "HIGH"


def _risk_style_name(score):
    try:
        v = float(score)
    except Exception:
        return "body"
    if v >= 70:
        return "risk_low"
    if v >= 40:
        return "risk_med"
    return "risk_high"


# ── Cover block ───────────────────────────────────────────────────────────────────
def _cover_block(story, s, title: str, subtitle: str, generated: str, meta_lines: list):
    """Dark cover header block."""
    # Dark rectangle via a 1-row table acting as a banner
    banner_data = [[""]]
    banner = Table(banner_data, colWidths=[19 * cm], rowHeights=[5.5 * cm])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 28),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 28),
        ("LEFTPADDING",   (0, 0), (-1, -1), 28),
    ]))
    story.append(banner)
    story.append(Spacer(1, -5.5 * cm))  # overlay text on top of banner

    # Title text inside banner — use a nested table so padding lines up
    inner = [[
        Paragraph(title, s["cover_title"]),
    ]]
    inner_t = Table(inner, colWidths=[17 * cm])
    inner_t.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 28),
        ("TOPPADDING",   (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("BACKGROUND",   (0, 0), (-1, -1), colors.transparent),
    ]))
    story.append(inner_t)

    sub_inner = [[Paragraph(subtitle, s["cover_sub"])]]
    sub_t = Table(sub_inner, colWidths=[17 * cm])
    sub_t.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 28),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ("BACKGROUND",   (0, 0), (-1, -1), colors.transparent),
    ]))
    story.append(sub_t)

    meta_text = "  ·  ".join(meta_lines)
    meta_inner = [[Paragraph(meta_text, s["cover_meta"])]]
    meta_t = Table(meta_inner, colWidths=[17 * cm])
    meta_t.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 28),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ("BACKGROUND",   (0, 0), (-1, -1), colors.transparent),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 0.8 * cm))


# ── Section divider ───────────────────────────────────────────────────────────────
def _section(story, s, label: str):
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(label.upper(), s["section_head"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=6))


# ── KPI summary row ───────────────────────────────────────────────────────────────
def _kpi_row(story, s, kpis: list):
    """
    kpis: list of (label, value, color_hex_or_None) tuples.
    Renders as a single-row table of metric boxes.
    """
    n = len(kpis)
    col_w = 19 * cm / n

    header_row = []
    value_row  = []
    for label, value, clr in kpis:
        val_style = ParagraphStyle(
            "kpi_dyn",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor(clr) if clr else C_DARK,
            alignment=TA_CENTER,
        )
        value_row.append(Paragraph(str(value), val_style))
        header_row.append(Paragraph(label.upper(), s["kpi_label"]))

    tbl = Table(
        [value_row, header_row],
        colWidths=[col_w] * n,
        rowHeights=[32, 18],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_SURFACE),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, 0), 14),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("LINEAFTER",     (0, 0), (-2, -1), 0.5, C_BORDER),
        ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ROUNDEDCORNERS",(0, 0), (-1, -1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.4 * cm))


# ── Generic data table ────────────────────────────────────────────────────────────
def _data_table(story, s, headers: list, rows: list, col_widths=None):
    """
    headers: list of column names.
    rows: list of lists of cell values.
    """
    n_cols = len(headers)
    if col_widths is None:
        col_widths = [19 * cm / n_cols] * n_cols

    head_cells = [Paragraph(h, s["table_head"]) for h in headers]
    data = [head_cells]
    for row in rows:
        data.append([Paragraph(str(c), s["table_cell"]) for c in row])

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    row_colors = []
    for i in range(1, len(data)):
        bg = C_WHITE if i % 2 == 1 else C_SURFACE
        row_colors.append(("BACKGROUND", (0, i), (-1, i), bg))

    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), C_DARK),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.4, C_BORDER),
        ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
        *row_colors,
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.3 * cm))


# ── Page footer callback ──────────────────────────────────────────────────────────
def _on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(C_MUTED)
    canvas.drawString(2 * cm, 1.2 * cm,
                      "DBAS — Driving Behaviour Analysis System  ·  DTW + SVM Classification Engine")
    canvas.drawRightString(w - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(2 * cm, 1.6 * cm, w - 2 * cm, 1.6 * cm)
    canvas.restoreState()


# ── ReportGenerator class ─────────────────────────────────────────────────────────
class ReportGenerator:
    def __init__(self):
        self.cfg = Config.load()
        os.makedirs(self.cfg.REPORTS_PATH, exist_ok=True)

    # ── Fleet report ─────────────────────────────────────────────────────────────
    def generate_fleet_report(self, comp_df) -> str:
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(self.cfg.REPORTS_PATH, f"fleet_report_{ts}.pdf")

        doc = SimpleDocTemplate(
            out_path,
            pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm,  bottomMargin=2.5 * cm,
        )
        s     = _styles()
        story = []
        now   = datetime.now().strftime("%d %b %Y  %H:%M")

        # ── Cover ──
        _cover_block(
            story, s,
            title="Fleet Safety Report",
            subtitle="Driving Behaviour Analysis System",
            generated=now,
            meta_lines=[
                f"Generated: {now}",
                f"Vehicles: {len(comp_df)}",
                "DBAS v1.0",
            ],
        )

        # ── Fleet KPIs ──
        _section(story, s, "Fleet Summary")

        total_trips   = int(comp_df["total_trips"].sum())     if "total_trips"      in comp_df.columns else 0
        avg_score     = comp_df["avg_safety_score"].mean()    if "avg_safety_score" in comp_df.columns else 0.0
        avg_agg       = comp_df["pct_aggressive"].mean()      if "pct_aggressive"   in comp_df.columns else 0.0
        n_vehicles    = len(comp_df)

        sc_color  = "#00c96e" if avg_score >= 70 else ("#f5a623" if avg_score >= 40 else "#ff3b5c")
        ag_color  = "#00c96e" if avg_agg   < 10  else ("#f5a623" if avg_agg   < 25  else "#ff3b5c")

        _kpi_row(story, s, [
            ("Total Vehicles",    n_vehicles,                "#1d6ff3"),
            ("Total Trips",       total_trips,               "#1d6ff3"),
            ("Fleet Avg Score",   f"{avg_score:.1f}",        sc_color),
            ("Avg Aggressive %",  f"{avg_agg:.1f}%",         ag_color),
        ])

        # ── Per-vehicle breakdown table ──
        _section(story, s, "Per-Vehicle Breakdown")

        COLUMNS = ["vehicle_id", "total_trips", "avg_safety_score", "pct_aggressive", "best_trip", "worst_trip"]
        HEADERS = ["Vehicle ID", "Trips", "Avg Score", "Aggressive %", "Best Trip", "Worst Trip"]
        COL_W   = [3.8*cm, 2.2*cm, 2.6*cm, 3.0*cm, 2.5*cm, 2.5*cm]

        present_cols = [c for c in COLUMNS if c in comp_df.columns]
        present_hdrs = [HEADERS[COLUMNS.index(c)] for c in present_cols]
        present_widths = [COL_W[COLUMNS.index(c)] for c in present_cols]

        # Build rows with colour-coded score cells
        head_cells = [Paragraph(h, s["table_head"]) for h in present_hdrs]
        data = [head_cells]

        for _, row in comp_df.iterrows():
            cells = []
            for col in present_cols:
                val = row.get(col, "")
                if col == "avg_safety_score":
                    clr = _score_color(val)
                    cell_style = ParagraphStyle(
                        "score_cell", fontName="Helvetica-Bold",
                        fontSize=9, textColor=clr, alignment=TA_CENTER,
                    )
                    cells.append(Paragraph(f"{float(val):.1f}", cell_style))
                elif col == "pct_aggressive":
                    clr = C_RED if float(val) > 25 else (C_AMBER if float(val) > 10 else C_GREEN)
                    cell_style = ParagraphStyle(
                        "agg_cell", fontName="Helvetica-Bold",
                        fontSize=9, textColor=clr, alignment=TA_CENTER,
                    )
                    cells.append(Paragraph(f"{float(val):.1f}%", cell_style))
                elif col in ("best_trip", "worst_trip"):
                    cells.append(Paragraph(f"{float(val):.1f}", s["table_cell"]))
                elif col == "total_trips":
                    cells.append(Paragraph(str(int(val)), s["table_cell"]))
                else:
                    cells.append(Paragraph(str(val), s["table_cell_left"]))
            data.append(cells)

        row_colors = []
        for i in range(1, len(data)):
            bg = C_WHITE if i % 2 == 1 else C_SURFACE
            row_colors.append(("BACKGROUND", (0, i), (-1, i), bg))

        tbl = Table(data, colWidths=present_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), C_DARK),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.4, C_BORDER),
            ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
            *row_colors,
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.4 * cm))

        # ── Risk summary ──
        _section(story, s, "Risk Assessment")

        high_risk = comp_df[comp_df["avg_safety_score"] < 40] if "avg_safety_score" in comp_df.columns else comp_df.head(0)
        mod_risk  = comp_df[(comp_df["avg_safety_score"] >= 40) & (comp_df["avg_safety_score"] < 70)] if "avg_safety_score" in comp_df.columns else comp_df.head(0)
        low_risk  = comp_df[comp_df["avg_safety_score"] >= 70] if "avg_safety_score" in comp_df.columns else comp_df

        risk_data = [
            [Paragraph("RISK LEVEL", s["table_head"]),
             Paragraph("VEHICLES", s["table_head"]),
             Paragraph("RECOMMENDATION", s["table_head"])],
            [Paragraph("HIGH", ParagraphStyle("rh", fontName="Helvetica-Bold", fontSize=10, textColor=C_RED, alignment=TA_CENTER)),
             Paragraph(str(len(high_risk)), s["table_cell"]),
             Paragraph("Immediate intervention required. Review trip history.", s["table_cell"])],
            [Paragraph("MODERATE", ParagraphStyle("rm", fontName="Helvetica-Bold", fontSize=10, textColor=C_AMBER, alignment=TA_CENTER)),
             Paragraph(str(len(mod_risk)), s["table_cell"]),
             Paragraph("Monitor closely. Consider driver coaching.", s["table_cell"])],
            [Paragraph("LOW", ParagraphStyle("rl", fontName="Helvetica-Bold", fontSize=10, textColor=C_GREEN, alignment=TA_CENTER)),
             Paragraph(str(len(low_risk)), s["table_cell"]),
             Paragraph("Driving behaviour is safe. Continue monitoring.", s["table_cell"])],
        ]
        risk_tbl = Table(risk_data, colWidths=[3.5*cm, 2.5*cm, 13*cm])
        risk_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), C_DARK),
            ("BACKGROUND",    (0, 1), (-1, 1), colors.HexColor("#fff0f2")),
            ("BACKGROUND",    (0, 2), (-1, 2), colors.HexColor("#fffbeb")),
            ("BACKGROUND",    (0, 3), (-1, 3), colors.HexColor("#f0fdf6")),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.4, C_BORDER),
            ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
        ]))
        story.append(risk_tbl)
        story.append(Spacer(1, 0.5 * cm))

        # ── Footer note ──
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(
            f"This report was automatically generated by DBAS v1.0 on {now}. "
            "Data is sourced from the on-device trip history. "
            "Classification uses Dynamic Time Warping (DTW) feature extraction and SVM modelling.",
            s["body_small"],
        ))

        doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
        return out_path

    # ── Trip report ──────────────────────────────────────────────────────────────
    def generate_trip_report(self, vehicle_id: str, scored_df) -> str:
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(self.cfg.REPORTS_PATH, f"trip_report_{vehicle_id}_{ts}.pdf")

        doc = SimpleDocTemplate(
            out_path,
            pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm,  bottomMargin=2.5 * cm,
        )
        s     = _styles()
        story = []
        now   = datetime.now().strftime("%d %b %Y  %H:%M")

        # ── Cover ──
        _cover_block(
            story, s,
            title=f"Trip Report",
            subtitle=f"Vehicle: {vehicle_id}",
            generated=now,
            meta_lines=[
                f"Generated: {now}",
                f"Vehicle ID: {vehicle_id}",
                f"Trips: {len(scored_df)}",
                "DBAS v1.0",
            ],
        )

        # ── Trip KPIs ──
        _section(story, s, "Trip Summary")

        n_trips   = len(scored_df)
        n_calm    = int((scored_df["label"] == "calm").sum())    if "label"        in scored_df.columns else 0
        n_agg     = int((scored_df["label"] == "aggressive").sum()) if "label"     in scored_df.columns else 0
        avg_score = scored_df["safety_score"].mean()             if "safety_score" in scored_df.columns else 0.0
        pct_agg   = (n_agg / n_trips * 100)                     if n_trips > 0    else 0.0
        best      = scored_df["safety_score"].max()              if "safety_score" in scored_df.columns else 0.0
        worst     = scored_df["safety_score"].min()              if "safety_score" in scored_df.columns else 0.0

        sc_color = "#00c96e" if avg_score >= 70 else ("#f5a623" if avg_score >= 40 else "#ff3b5c")
        ag_color = "#00c96e" if pct_agg   < 10  else ("#f5a623" if pct_agg   < 25  else "#ff3b5c")

        _kpi_row(story, s, [
            ("Total Trips",    n_trips,              "#1d6ff3"),
            ("Calm Trips",     n_calm,               "#00c96e"),
            ("Aggressive",     n_agg,                "#ff3b5c"),
            ("Avg Score",      f"{avg_score:.1f}",   sc_color),
            ("Aggressive %",   f"{pct_agg:.1f}%",    ag_color),
        ])

        # ── Risk assessment card ──
        _section(story, s, "Vehicle Risk Assessment")

        if avg_score < 40 or pct_agg > 60:
            risk_bg   = colors.HexColor("#fff0f2")
            risk_text = "HIGH RISK"
            risk_clr  = C_RED
            risk_desc = "High-risk driving patterns detected. Immediate coaching or intervention is recommended."
        elif avg_score < 70 or pct_agg > 35:
            risk_bg   = colors.HexColor("#fffbeb")
            risk_text = "MODERATE RISK"
            risk_clr  = C_AMBER
            risk_desc = "Moderate-risk patterns observed. Monitoring and targeted coaching advised."
        else:
            risk_bg   = colors.HexColor("#f0fdf6")
            risk_text = "LOW RISK"
            risk_clr  = C_GREEN
            risk_desc = "Driving behaviour is safe and consistent. Continue regular monitoring."

        risk_style = ParagraphStyle(
            "risk_dyn", fontName="Helvetica-Bold",
            fontSize=13, textColor=risk_clr, alignment=TA_LEFT,
        )
        risk_data = [[
            Paragraph(risk_text, risk_style),
            Paragraph(risk_desc, s["body"]),
        ]]
        risk_card = Table(risk_data, colWidths=[4 * cm, 15 * cm])
        risk_card.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), risk_bg),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING",   (0, 0), (-1, -1), 14),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
            ("LINEAFTER",     (0, 0), (0, -1), 1, risk_clr),
            ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
        ]))
        story.append(risk_card)
        story.append(Spacer(1, 0.4 * cm))

        # ── Score range ──
        _section(story, s, "Score Range")
        _kpi_row(story, s, [
            ("Best Trip Score",  f"{best:.1f}",  "#00c96e"),
            ("Worst Trip Score", f"{worst:.1f}", "#ff3b5c"),
            ("Score Range",      f"{best - worst:.1f}", "#1d6ff3"),
        ])

        # ── Trip-by-trip table ──
        _section(story, s, "Trip-by-Trip Detail")

        display_cols = []
        if "trip_id"      in scored_df.columns: display_cols.append("trip_id")
        if "label"        in scored_df.columns: display_cols.append("label")
        if "confidence"   in scored_df.columns: display_cols.append("confidence")
        if "safety_score" in scored_df.columns: display_cols.append("safety_score")
        if "timestamp"    in scored_df.columns: display_cols.append("timestamp")

        col_map = {
            "trip_id":      ("Trip ID",       2.8 * cm),
            "label":        ("Label",         2.8 * cm),
            "confidence":   ("Confidence",    3.0 * cm),
            "safety_score": ("Safety Score",  3.2 * cm),
            "timestamp":    ("Timestamp",     7.2 * cm),
        }
        headers   = [col_map[c][0] for c in display_cols]
        col_widths = [col_map[c][1] for c in display_cols]

        head_row = [Paragraph(h, s["table_head"]) for h in headers]
        data = [head_row]

        for _, row in scored_df.iterrows():
            cells = []
            for col in display_cols:
                val = row.get(col, "")
                if col == "safety_score":
                    clr = _score_color(val)
                    cell_s = ParagraphStyle(
                        "sc", fontName="Helvetica-Bold",
                        fontSize=9, textColor=clr, alignment=TA_CENTER,
                    )
                    cells.append(Paragraph(f"{float(val):.1f}", cell_s))
                elif col == "label":
                    clr = C_GREEN if str(val) == "calm" else C_RED
                    cell_s = ParagraphStyle(
                        "lbl", fontName="Helvetica-Bold",
                        fontSize=9, textColor=clr, alignment=TA_CENTER,
                    )
                    cells.append(Paragraph(str(val).upper(), cell_s))
                elif col == "confidence":
                    cells.append(Paragraph(f"{float(val):.3f}", s["table_cell"]))
                else:
                    cells.append(Paragraph(str(val), s["table_cell"]))
            data.append(cells)

        row_bgs = []
        for i in range(1, len(data)):
            bg = C_WHITE if i % 2 == 1 else C_SURFACE
            row_bgs.append(("BACKGROUND", (0, i), (-1, i), bg))

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), C_DARK),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.4, C_BORDER),
            ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
            *row_bgs,
        ]))
        story.append(tbl)

        # ── Footer note ──
        story.append(Spacer(1, 0.6 * cm))
        story.append(Paragraph(
            f"This report was automatically generated by DBAS v1.0 on {now}. "
            "Classification uses Dynamic Time Warping (DTW) feature extraction and SVM modelling.",
            s["body_small"],
        ))

        doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
        return out_path
