from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from get_answer.config import RAGConfig


def create_pdf(content: str, filename: str, config: RAGConfig) -> None:
    try:
        pdfmetrics.registerFont(TTFont(config.font_name, config.font_path))
    except Exception as exc:
        raise FileNotFoundError(
            f"Cannot register font '{config.font_name}' from '{config.font_path}'."
        ) from exc

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    style = styles["Normal"]
    style.fontSize = 12
    style.leading = 14
    style.fontName = config.font_name

    paragraphs = []
    for line in content.split("\n"):
        if line.strip():
            paragraphs.append(Paragraph(line, style))
            paragraphs.append(Spacer(1, 12))
        else:
            paragraphs.append(Spacer(1, 12))

    doc.build(paragraphs)
