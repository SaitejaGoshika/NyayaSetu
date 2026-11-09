from __future__ import annotations

import json
import sqlite3
from io import BytesIO
from pathlib import Path
from typing import Any

from docx import Document
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse

from backend.api.dependencies import get_current_user
from backend.models.schemas import DocumentRecord
from backend.services import database as database_service
from backend.services.database import get_db

router = APIRouter(prefix="/api")


@router.get("/documents", response_model=list[DocumentRecord])
def list_documents(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> list[DocumentRecord]:
    rows = db.execute(
        "SELECT document_id, filename, created_at, status FROM documents WHERE owner_uid = ? ORDER BY created_at DESC",
        (str(current_user["uid"]),),
    ).fetchall()
    return [DocumentRecord(**dict(row)) for row in rows]


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> FileResponse:
    row = db.execute(
        "SELECT filename, storage_name FROM documents WHERE document_id = ? AND owner_uid = ?",
        (document_id, str(current_user["uid"])),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "document_not_found", "message": "The requested document was not found."})

    root = database_service.DOCUMENT_STORAGE_DIR.resolve()
    storage_name = str(row["storage_name"])
    file_path = (root / storage_name).resolve()
    if file_path.parent != root or not file_path.is_file():
        raise HTTPException(status_code=404, detail={"code": "document_file_missing", "message": "The local document file could not be found."})

    safe_name = str(row["filename"]).replace('"', "'")
    return FileResponse(file_path, filename=safe_name, media_type="application/octet-stream")


@router.get("/analyze/{document_id}/report")
def export_analysis_report(
    document_id: str,
    format: str = "pdf",
    current_user: dict[str, Any] = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> Response:
    row = db.execute(
        "SELECT filename FROM documents WHERE document_id = ? AND owner_uid = ?",
        (document_id, str(current_user["uid"])),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "document_not_found", "message": "The requested document was not found."})

    analysis = db.execute(
        "SELECT extracted_text, findings_json, rules_version, created_at FROM analyses WHERE document_id = ? AND owner_uid = ? ORDER BY created_at DESC LIMIT 1",
        (document_id, str(current_user["uid"])),
    ).fetchone()
    if analysis is None:
        raise HTTPException(status_code=404, detail={"code": "analysis_not_found", "message": "No analysis is available for this document."})

    findings = json.loads(analysis["findings_json"])
    title = str(row["filename"])
    safe_title = title.rsplit(".", 1)[0] if "." in title else title
    extension = format.lower()
    if extension not in {"pdf", "docx"}:
        raise HTTPException(status_code=400, detail={"code": "invalid_report_format", "message": "Report format must be 'pdf' or 'docx'."})

    if extension == "docx":
        report_doc = Document()
        report_doc.add_heading(f"NyayaSetu contract review: {title}", level=1)
        report_doc.add_paragraph(f"Date: {analysis['created_at']}")
        report_doc.add_paragraph(f"Rules version: {analysis['rules_version']}")
        report_doc.add_paragraph("Disclaimer: This report is a screening summary, not legal advice.")
        report_doc.add_paragraph("Summary of findings:")
        for finding in findings:
            risk_level = finding.get("riskLevel") or finding.get("risk_level") or "low"
            title = finding.get("title") or "Finding"
            legal_basis = finding.get("legalBasis") or finding.get("legal_basis") or "General contract risk"
            explanation = finding.get("explanation") or "No explanation recorded."
            match_text = finding.get("matchText") or finding.get("match_text") or ""
            report_doc.add_paragraph(f"- {title} ({risk_level})")
            report_doc.add_paragraph(f"  Basis: {legal_basis}")
            report_doc.add_paragraph(f"  Explanation: {explanation}")
            report_doc.add_paragraph(f"  Match: {match_text[:250]}")
        buffer = BytesIO()
        report_doc.save(buffer)
        payload = buffer.getvalue()
        headers = {"Content-Disposition": f'attachment; filename="{safe_title}.docx"'}
        return Response(content=payload, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers=headers)

    try:
        from fpdf import FPDF
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"code": "pdf_export_unavailable", "message": "PDF report generation is not available in this environment."}) from exc

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, f"NyayaSetu contract review: {title}")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8, f"Date: {analysis['created_at']}\nRules version: {analysis['rules_version']}\nDisclaimer: This report is a screening summary, not legal advice.")

    for finding in findings:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        title = str(finding.get("title") or "Finding").encode("latin-1", "replace").decode("latin-1")
        risk_level = str(finding.get("riskLevel") or finding.get("risk_level") or "low").upper()
        pdf.multi_cell(0, 8, f"{title} ({risk_level})")
        pdf.set_font("Helvetica", "", 10)
        legal_basis = str(finding.get("legalBasis") or finding.get("legal_basis") or "").encode("latin-1", "replace").decode("latin-1")
        explanation = str(finding.get("explanation") or "").encode("latin-1", "replace").decode("latin-1")
        match_text = str(finding.get("matchText") or finding.get("match_text") or "").encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, f"Legal basis: {legal_basis}")
        pdf.multi_cell(0, 6, f"Explanation: {explanation}")
        pdf.multi_cell(0, 6, f"Match: {match_text[:200]}")

    payload = pdf.output(dest="S")
    return Response(content=payload, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{safe_title}.pdf"'})


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> Response:
    row = db.execute(
        "SELECT storage_name FROM documents WHERE document_id = ? AND owner_uid = ?",
        (document_id, str(current_user["uid"])),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "document_not_found", "message": "The requested document was not found."})

    root = database_service.DOCUMENT_STORAGE_DIR.resolve()
    file_path = (root / str(row["storage_name"])).resolve()
    if file_path.parent != root:
        raise HTTPException(status_code=404, detail={"code": "document_not_found", "message": "The requested document was not found."})

    db.execute("DELETE FROM documents WHERE document_id = ? AND owner_uid = ?", (document_id, str(current_user["uid"])))
    db.commit()
    if file_path.exists():
        file_path.unlink()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
