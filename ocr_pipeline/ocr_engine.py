import os
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import pytesseract

from ocr_pipeline.text_cleaner import (
    apply_safe_macedonian_fixes,
    average_confidence,
    detect_suspicious_tokens,
    normalize_ocr_text,
)

_default_tesseract = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if sys.platform == "win32"
    else "/usr/bin/tesseract"
)
TESSERACT_CMD = os.getenv("TESSERACT_CMD", _default_tesseract)

if Path(TESSERACT_CMD).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def _resize_image(gray: np.ndarray, target_min_width: int = 1800) -> np.ndarray:
    height, width = gray.shape

    if width >= target_min_width:
        return gray

    scale = target_min_width / width
    new_size = (int(width * scale), int(height * scale))
    return cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)


def _decode_to_gray(image_bytes: bytes) -> np.ndarray:
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Invalid image file.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return _resize_image(gray)


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    gray = _decode_to_gray(image_bytes)
    denoised = cv2.medianBlur(gray, 3)

    thresholded = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        101,
        15,
    )

    return thresholded


def extract_text_from_image(image_bytes: bytes, language: str = "mkd") -> dict:
    processed_image = preprocess_image(image_bytes)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_path = temp_file.name

        Image.fromarray(processed_image).save(temp_path, format="PNG")

        config = "--oem 3 --psm 3"

        raw_text = pytesseract.image_to_string(
            temp_path,
            lang=language,
            config=config,
        ).strip()

        data = pytesseract.image_to_data(
            temp_path,
            lang=language,
            config=config,
            output_type=pytesseract.Output.DICT,
        )

        cleaned_text = normalize_ocr_text(raw_text)
        cleaned_text = apply_safe_macedonian_fixes(cleaned_text)

        return {
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "avg_confidence": average_confidence(data),
            "suspicious_tokens": detect_suspicious_tokens(data),
            "language_used": language,
            "preprocessing_used": "adaptive_threshold",
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
