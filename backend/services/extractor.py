from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

import pdfplumber
from docx import Document

from backend.services.errors import ExtractionError

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}
OCR_ENABLED = os.getenv("OCR_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng+hin+tel")
OCR_MAX_PAGES = max(1, int(os.getenv("OCR_MAX_PAGES", "5")))


def _ocr_pdf_text(path: Path) -> str:
    if not OCR_ENABLED:
        return ""
    try:
        import pytesseract
    except Exception:
        return ""

    try:
        from PIL import Image
    except Exception:
        return ""

    texts: list[str] = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages[:OCR_MAX_PAGES]:
                extracted = page.extract_text() or ""
                if extracted.strip():
                    texts.append(extracted.strip())
                    continue
                try:
                    image = page.to_image(resolution=200).original
                except Exception:
                    continue
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                buffer.seek(0)
                ocr_text = pytesseract.image_to_string(Image.open(buffer), lang=OCR_LANGUAGES)
                if ocr_text.strip():
                    texts.append(ocr_text.strip())
    except Exception:
        return ""
    return "\n\n".join(texts).strip()


def extract_text(file_path: str | Path, extension: str) -> str:
    normalized_extension = extension.lower()
    if normalized_extension not in SUPPORTED_EXTENSIONS:
        raise ExtractionError(415, "unsupported_media_type", "Only PDF and DOCX files are supported.")

    path = Path(file_path)
    if not path.is_file():
        raise ExtractionError(400, "invalid_document", "The uploaded document could not be read.")

    try:
        if normalized_extension == ".pdf":
            with pdfplumber.open(path) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            text = "\n\n".join(page for page in pages if page.strip()).strip()
            if not text:
                text = _ocr_pdf_text(path)
            return text

        document = Document(path)
        sections = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        for table in document.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                if any(cells):
                    sections.append(" | ".join(cells))
        return "\n".join(sections).strip()
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(
            400,
            "corrupted_document",
            "The document is corrupted, encrypted, or could not be parsed.",
        ) from exc
