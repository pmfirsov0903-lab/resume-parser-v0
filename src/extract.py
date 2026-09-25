"""Витяг тексту з резюме у форматах PDF та DOCX."""

from pathlib import Path

import docx
import pdfplumber

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix == ".docx":
        return _extract_docx(path)
    raise ValueError(f"Непідтримуваний формат файлу: {suffix}")


def _extract_pdf(path: Path) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_docx(path: Path) -> str:
    document = docx.Document(path)
    return "\n".join(p.text for p in document.paragraphs if p.text)
