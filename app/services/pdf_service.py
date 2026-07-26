"""
app/services/pdf_service.py
------------------------------
PDF report generation using ReportLab. Produces a professional, letterhead
style report for a Project (hierarchy summary + equipment status table),
suitable for printing / sharing with clients such as NTPC / NPCIL.
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)


class PDFService:

    @staticmethod
    def generate_project_report(project) -> io.BytesIO:
        """Generate a full progress report PDF for the given Project object."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=landscape(A4),
            topMargin=1.2 * cm, bottomMargin=1.2 * cm,
            leftMargin=1.2 * cm, rightMargin=1.2 * cm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#1F3864")
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#555555")
        )
        section_style = ParagraphStyle(
            "SectionHeader", parent=styles["Heading2"], fontSize=13, textColor=colors.HexColor("#1F3864"),
            spaceBefore=12, spaceAfter=6,
        )

        elements = []
        elements.append(Paragraph("BHEL Project Monitoring System", title_style))
        elements.append(Paragraph("Bharat Heavy Electricals Limited &mdash; Project Progress Report", subtitle_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d-%b-%Y %H:%M')}", subtitle_style))
        elements.append(Spacer(1, 0.5 * cm))

        # --- Project summary table ---
        elements.append(Paragraph(f"Project: {project.name} ({project.project_code})", section_style))
        summary_data = [
            ["Client", project.client_name or "-", "Location", project.location or "-"],
            ["Capacity (MW)", project.capacity_mw or "-", "Status", project.status],
            [
                "Start Date",
                project.start_date.strftime("%d-%b-%Y") if project.start_date else "-",
                "Scheduled End",
                project.scheduled_end_date.strftime("%d-%b-%Y") if project.scheduled_end_date else "-",
            ],
            ["Project Manager", project.project_manager or "-", "Overall Progress", f"{project.overall_progress or 0}%"],
        ]
        summary_table = Table(summary_data, colWidths=[4 * cm, 8 * cm, 4 * cm, 8 * cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2F8")),
            ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EEF2F8")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.6 * cm))

        # --- Equipment detail table ---
        elements.append(Paragraph("Equipment Progress Detail", section_style))
        header = ["Unit", "Area", "System", "Equipment", "Status", "Install %", "Commission %", "Engineer"]
        rows = [header]
        for unit in project.units:
            for area in unit.areas:
                for system in area.systems:
                    for eq in system.equipment_items:
                        rows.append([
                            unit.unit_code, area.area_code, system.system_code,
                            f"{eq.equipment_code} - {eq.equipment_name}"[:40],
                            eq.status,
                            f"{eq.installation_progress or 0:.0f}%",
                            f"{eq.commissioning_progress or 0:.0f}%",
                            eq.assigned_engineer.full_name if eq.assigned_engineer else "-",
                        ])

        if len(rows) == 1:
            rows.append(["-", "-", "-", "No equipment records found", "-", "-", "-", "-"])

        detail_table = Table(rows, repeatRows=1, colWidths=[2.2*cm, 2.5*cm, 3*cm, 7*cm, 3.2*cm, 2.2*cm, 2.6*cm, 3.5*cm])
        detail_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FC")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(detail_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer
