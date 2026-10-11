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

