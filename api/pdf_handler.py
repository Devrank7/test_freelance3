import io
import os
import uuid
from abc import ABC, abstractmethod

import fitz
from dotenv import load_dotenv
from fastapi import UploadFile
from pymupdf import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas

from api.pdf_convert import convert_text_from_pdf, PDFConverterFreelance

load_dotenv()
SAVE_PATH = os.getenv('SAVE_PATH')

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


async def get_pdf_stream(upload_pdf_file: UploadFile) -> io.BytesIO:
    contents = await upload_pdf_file.read()
    return io.BytesIO(contents)


def path_file(filename: str):
    id_file = uuid.uuid4().hex
    path_for = f"modified_{id_file}_{filename}"
    modified_pdf_path = os.path.join(SAVE_PATH, path_for)
    return modified_pdf_path, path_for


class PdfHandler(ABC):
    @abstractmethod
    async def save_pdf(self):
        pass


class PDFHandlerImpl(PdfHandler):

    def __init__(self, upload_pdf_file: UploadFile):
        self.upload_pdf_file = upload_pdf_file

    async def save_pdf(self):
        with fitz.open(stream=await get_pdf_stream(self.upload_pdf_file), filetype="pdf") as pdf:
            text_to_add = f"Filename: {self.upload_pdf_file.filename}"
            pdf.insert_page(-1, text=text_to_add, fontsize=12)
            modified_pdf_path, path_for = path_file(self.upload_pdf_file.filename)
            pdf.save(modified_pdf_path)
        return path_for


class PDFHandlerStrict(PdfHandler):
    font_path = "fonts/DejaVuSansMono-Oblique.ttf"

    def __init__(self, upload_pdf_file: UploadFile):
        self.upload_pdf_file = upload_pdf_file

    def extract_text(self, pdf: Document):
        original_text = ""
        for page in pdf:
            original_text += page.get_text()
        return original_text

    def draw_pdf(self, text: str, pdf: Canvas):
        lines = text.split('\n')
        x, y = 100, 750
        for line in lines:
            pdf.drawString(x, y, line)
            y -= 15

    def save_pdf_file(self, modified_pdf_path: str, text: str):
        pdf = canvas.Canvas(modified_pdf_path, pagesize=A4)
        pdfmetrics.registerFont(TTFont("DejaVuSans", self.font_path))
        pdf.setFont("DejaVuSans", 12)
        self.draw_pdf(text, pdf)
        pdf.showPage()
        pdf.save()

    async def save_pdf(self):
        with fitz.open(stream=await get_pdf_stream(self.upload_pdf_file), filetype="pdf") as pdf:
            new_text = convert_text_from_pdf(PDFConverterFreelance(original_text=self.extract_text(pdf)))
            modified_pdf_path, path_for = path_file(self.upload_pdf_file.filename)
            self.save_pdf_file(modified_pdf_path, new_text)
        return path_for


async def handle_pdf(pdf_strategy_handler: PdfHandler):
    return await pdf_strategy_handler.save_pdf()
