import io
import os
import tempfile
from pathlib import Path

from PIL import Image
import pytesseract


TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if Path(TESSERACT_CMD).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def extract_text_from_image(image_bytes: bytes, language: str = "mkd") -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as exc:
        raise ValueError("Invalid image file.") from exc

    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_path = temp_file.name

        image.save(temp_path, format="PNG")

        text = pytesseract.image_to_string(temp_path, lang=language)
        return text.strip()

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)