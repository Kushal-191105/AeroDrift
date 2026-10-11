import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, HRFlowable

logger = logging.getLogger(__name__)

class PDFIncidentReportGenerator:
    """Generates enterprise-grade incident audit reports in PDF format."""
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)


    def _build_header(self, incident_id: str, timestamp_str: str) -> list:
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1A365D"),
            alignment=0
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#4A5568")
        )
        
        elements = [
            Paragraph("AeroDrift Incident & Autonomous Remediation Report", title_style),
            Paragraph(f"Autonomous CloudOps Daemon | Security Incident ID: <b>{incident_id}</b> | Timestamp: {timestamp_str}", subtitle_style),
            Spacer(1, 12),
            HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2B6CB0"), spaceAfter=15),
        ]
        return elements


    def _build_incident_summary_table(self, target: str, path: list, latency_ms: float) -> list:
        styles = getSampleStyleSheet()
        heading_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, leading=18, textColor=colors.HexColor("#2D3748"))
        
        data = [
            ["Metric / Field", "Incident Details"],
            ["Security Severity", "CRITICAL (Unauthorized Ingress Route)"],
            ["Target Cloud Resource", target],
            ["Compromised Network Vector", " ➡️  ".join(path)],
            ["Autonomous Action Taken", "AST-Synthesized revoke_security_group_ingress"],
            ["Self-Healing Latency", f"{latency_ms:.2f} ms"],
            ["Remediation Status", "RESOLVED & VERIFIED"]
        ]
        
        t = Table(data, colWidths=[180, 320])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#2B6CB0")),
            ("TEXTCOLOR", (0, 0), (1, 0), colors.white),
            ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (1, 0), 6),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FAFC")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("TEXTCOLOR", (0, 1), (0, -1), colors.HexColor("#2D3748")),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        
        return [
            Paragraph("1. Incident Summary & Threat Analysis", heading_style),
            Spacer(1, 6),
            t,
            Spacer(1, 15)
        ]

