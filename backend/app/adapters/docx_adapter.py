from __future__ import annotations

import io
import zipfile

from app.adapters.document_adapter import DocumentAdapter
from app.exceptions.document_exceptions import DocumentValidationException


class DocxDocumentAdapter(DocumentAdapter):
    extension = "docx"
    mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def validate_integrity(self, content: bytes) -> None:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as docx_file:
                if "word/document.xml" not in docx_file.namelist():
                    raise DocumentValidationException(
                        "DOCX inválido: estrutura do documento não reconhecida."
                    )
        except zipfile.BadZipFile as exc:
            raise DocumentValidationException("DOCX inválido: arquivo corrompido.") from exc

    def extract_text(self, content: bytes) -> str:
        try:
            from docx import Document as DocxDocument

            document = DocxDocument(io.BytesIO(content))
        except ModuleNotFoundError as exc:
            raise DocumentValidationException(
                "Extração de DOCX indisponível: dependência python-docx não instalada."
            ) from exc
        except Exception as exc:
            raise DocumentValidationException("Falha ao extrair texto do DOCX.") from exc

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]
        extracted_text = "\n".join(paragraphs).strip()
        if not extracted_text:
            raise DocumentValidationException("DOCX válido, mas sem texto extraível.")
        return extracted_text[:200000]
