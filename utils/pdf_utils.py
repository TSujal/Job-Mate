from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import PyPDF2
from langchain_core.messages import HumanMessage


def generate_pdf(text: str) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Clean the text
    text = text.strip()

    # Only extract content starting from "Dear Hiring Manager"
    start_index = text.lower().find("dear hiring manager")
    if start_index != -1:
        text = text[start_index:]
    else:
        text = "Dear Hiring Manager,\n\n" + text  # Fallback if not found

    # Adjust line height for tighter spacing
    line_height = 6  # Adjust this value for the desired line spacing
    for line in text.split('\n'):
        pdf.multi_cell(0, line_height, line)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)


def extract_pdf_text(file) -> str:
    reader = PyPDF2.PdfReader(BytesIO(file.read()))
    return " ".join(page.extract_text() or "" for page in reader.pages).strip()


def timestamped_msg(content: str):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    return HumanMessage(content=f"{ts} {content}")
