import io
import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import pytesseract


TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if Path(TESSERACT_CMD).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Invalid image file.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    scaled = cv2.resize(gray, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)

    blurred = cv2.GaussianBlur(scaled, (3, 3), 0)

    processed = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return processed


def extract_text_from_image(image_bytes: bytes, language: str = "mkd") -> str:
    processed_image = preprocess_image(image_bytes)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_path = temp_file.name

        Image.fromarray(processed_image).save(temp_path, format="PNG")

        text = pytesseract.image_to_string(
            temp_path,
            lang=language,
            config="--oem 3 --psm 6"
        )
        return text.strip()

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)