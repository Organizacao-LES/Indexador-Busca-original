from __future__ import annotations

from abc import ABC, abstractmethod


class DocumentAdapter(ABC):
    extension: str
    mime_type: str

    @abstractmethod
    def validate_integrity(self, content: bytes) -> None:
        pass

    @abstractmethod
    def extract_text(self, content: bytes) -> str:
        pass
