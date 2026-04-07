from __future__ import annotations

from app.adapters.csv_adapter import CsvDocumentAdapter
from app.adapters.docx_adapter import DocxDocumentAdapter
from app.adapters.document_adapter import DocumentAdapter
from app.adapters.pdf_adapter import PdfDocumentAdapter
from app.adapters.txt_adapter import TxtDocumentAdapter
from app.exceptions.document_exceptions import DocumentValidationException


class DocumentAdapterRegistry:
    def __init__(self):
        self._adapters: dict[str, DocumentAdapter] = {}

    def register(self, adapter: DocumentAdapter) -> None:
        self._adapters[adapter.extension] = adapter

    def get(self, extension: str) -> DocumentAdapter:
        adapter = self._adapters.get(extension.lower())
        if adapter is None:
            raise DocumentValidationException("Não há adapter configurado para esse tipo de arquivo.")
        return adapter


document_adapter_registry = DocumentAdapterRegistry()
document_adapter_registry.register(PdfDocumentAdapter())
document_adapter_registry.register(DocxDocumentAdapter())
document_adapter_registry.register(TxtDocumentAdapter())
document_adapter_registry.register(CsvDocumentAdapter())
