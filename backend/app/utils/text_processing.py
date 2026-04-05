import re
import unicodedata


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def tokenize_text(text: str) -> list[str]:
    if not text:
        return []
    return [token for token in text.split(" ") if token]
