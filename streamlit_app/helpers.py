"""Simple calculations shared by the dashboard, calendar, and PDF report."""
from collections import Counter
from datetime import date, timedelta
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def due_date(assignment):
    """MongoDB sends dates like '2026-10-30T00:00:00.000Z'."""
    return date.fromisoformat(str(assignment["dueDate"])[:10])


def progress_stats(assignments, today=None):
    today = today or date.today()
    total = len(assignments)
    completed = sum(a["status"] == "Completed" for a in assignments)
    overdue = sum(a["status"] != "Completed" and due_date(a) < today for a in assignments)
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "overdue": overdue,
        "percent": round(completed / total * 100) if total else 0,
    }


def reminder_text(assignment, today=None):
    """Returns a reminder label, or None if this assignment is not urgent."""
    today = today or date.today()
    if assignment["status"] == "Completed":
        return None
    due = due_date(assignment)
    if due < today:
        return "Overdue"
    if due == today:
        return "Due today"
    if due == today + timedelta(days=1):
        return "Due tomorrow"
    return None


def make_pdf(assignments, user):
    """Return PDF bytes for Streamlit's Download button; no external web service."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    stats = progress_stats(assignments)
    content = [
        Paragraph("TaskTrack - Assignment Report", styles["Title"]),
        Paragraph(f"Student: {escape(user.get('name', 'Student'))}", styles["Normal"]),
        Paragraph(f"Email: {escape(user.get('email', ''))}", styles["Normal"]),
        Spacer(1, 14),
        Paragraph(
            f"Total: {stats['total']} | Completed: {stats['completed']} | "
            f"Overdue: {stats['overdue']} | Progress: {stats['percent']}%",
            styles["Heading3"],
        ),
        Spacer(1, 12),
    ]
    headers = ["Assignment", "Subject", "Due date", "Priority", "Status"]
    rows = [[Paragraph(text, styles["BodyText"]) for text in headers]]
    for a in sorted(assignments, key=due_date):
        values = [a.get("title", ""), a.get("subject", ""),
                  due_date(a).isoformat(), a.get("priority", ""), a.get("status", "")]
        rows.append([Paragraph(escape(str(v)), styles["BodyText"]) for v in values])
    if assignments:
        table = Table(rows, colWidths=[130, 100, 72, 70, 95], repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        content.append(table)
    else:
        content.append(Paragraph("No assignments yet.", styles["Normal"]))
    doc.build(content)
    return buffer.getvalue()
