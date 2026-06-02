from __future__ import annotations

from app.adapters.document_adapter import DocumentAdapter
from app.exceptions.document_exceptions import DocumentValidationException


class TxtDocumentAdapter(DocumentAdapter):
    extension = "txt"
    mime_type = "text/plain"

    def validate_integrity(self, content: bytes) -> None:
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentValidationException(
                "Arquivo de texto inválido: codificação UTF-8 obrigatória."
            ) from exc

    def extract_text(self, content: bytes) -> str:
        try:
            extracted_text = content.decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            raise DocumentValidationException(
                "Arquivo de texto inválido: codificação UTF-8 obrigatória."
            ) from exc

        if not extracted_text:
            raise DocumentValidationException("TXT válido, mas sem conteúdo textual.")
        return extracted_text[:200000]
