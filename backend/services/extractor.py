from __future__ import annotations

from pathlib import Path

import pdfplumber
from docx import Document

from backend.services.errors import ExtractionError

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


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
            return "\n\n".join(page for page in pages if page.strip()).strip()

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
