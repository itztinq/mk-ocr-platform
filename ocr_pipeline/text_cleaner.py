import re


def clean_ocr_text(text: str) -> str:
    if not text:
        return ""

    cleaned = text

    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    cleaned = re.sub(r"(\w)-\n(\w)", r"\1\2", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    cleaned = re.sub(r"[ ]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n[ ]+", "\n", cleaned)

    return cleaned.strip()