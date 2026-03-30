from __future__ import annotations

import csv

from app.adapters.document_adapter import DocumentAdapter
from app.exceptions.document_exceptions import DocumentValidationException


class CsvDocumentAdapter(DocumentAdapter):
    extension = "csv"
    mime_type = "text/csv"

    def validate_integrity(self, content: bytes) -> None:
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentValidationException(
                "Arquivo de texto inválido: codificação UTF-8 obrigatória."
            ) from exc

        try:
            rows = list(csv.reader(decoded.splitlines()))
        except csv.Error as exc:
            raise DocumentValidationException("CSV inválido: estrutura inconsistente.") from exc

        if not rows:
            raise DocumentValidationException("CSV inválido: arquivo sem registros.")

    def extract_text(self, content: bytes) -> str:
        try:
            decoded = content.decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            raise DocumentValidationException(
                "Arquivo de texto inválido: codificação UTF-8 obrigatória."
            ) from exc

        if not decoded:
            raise DocumentValidationException("CSV válido, mas sem conteúdo textual.")

        rows = list(csv.reader(decoded.splitlines()))
        flattened_rows = [", ".join(cell.strip() for cell in row if cell.strip()) for row in rows]
        extracted_text = "\n".join(row for row in flattened_rows if row).strip()
        if not extracted_text:
            raise DocumentValidationException("CSV válido, mas sem conteúdo textual.")
        return extracted_text[:200000]
