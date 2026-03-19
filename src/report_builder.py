import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def wrap_text(text, width=95):
    words = str(text).split()
    lines = []
    current = []

    for word in words:
        trial = " ".join(current + [word])
        if len(trial) <= width:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines


def build_pdf_report(output_path, report_title, insights, metrics, trend_results):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, report_title)

    y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Total Posts: {metrics.get('total_posts', 0)}")
    y -= 18
    c.drawString(50, y, f"Unique Subreddits: {metrics.get('unique_subreddits', 0)}")
    y -= 18
    c.drawString(50, y, f"Top Topic: {metrics.get('top_topic', 'N/A')}")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Executive Summary")
    y -= 18
    c.setFont("Helvetica", 10)

    for line in wrap_text(insights.get("executive_summary", "")):
        c.drawString(50, y, line)
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Top Themes")
    y -= 18
    c.setFont("Helvetica", 10)

    for theme in insights.get("top_themes", []):
        c.drawString(60, y, f"- {theme}")
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Source Shifts")
    y -= 18
    c.setFont("Helvetica", 10)

    for line in wrap_text(insights.get("source_shifts", "")):
        c.drawString(50, y, line)
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Response Focus")
    y -= 18
    c.setFont("Helvetica", 10)

    for line in wrap_text(insights.get("response_focus", "")):
        c.drawString(50, y, line)
        y -= 14

    spike_alert = trend_results.get("spike_alert")
    if spike_alert and y > 100:
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Spike Alert")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(
            50,
            y,
            f"Spike detected on {spike_alert['date']} | Size: {spike_alert['spike_size']} | Driver: {spike_alert['probable_topic_driver']}"
        )

    c.save()
    return output_path