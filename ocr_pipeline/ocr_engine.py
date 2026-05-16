import os
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


TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if Path(TESSERACT_CMD).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def _resize_image(gray: np.ndarray, target_min_width: int = 1800) -> np.ndarray:
    height, width = gray.shape

    if width >= target_min_width:
        return gray

    scale = target_min_width / width
    new_size = (int(width * scale), int(height * scale))
    return cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)


def _deskew_image(binary_image: np.ndarray) -> np.ndarray:
    inverted = cv2.bitwise_not(binary_image)
    coords = np.column_stack(np.where(inverted > 0))

    if len(coords) == 0:
        return binary_image

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90

    if abs(angle) < 0.3:
        return binary_image

    h, w = binary_image.shape[:2]
    center = (w // 2, h // 2)

    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    return cv2.warpAffine(
        binary_image,
        rotation_matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Invalid image file.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = _resize_image(gray)

    denoised = cv2.medianBlur(gray, 3)

    normalized = cv2.normalize(denoised, None, 0, 255, cv2.NORM_MINMAX)

    thresholded = cv2.adaptiveThreshold(
        normalized,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15,
    )

    deskewed = _deskew_image(thresholded)
    return deskewed


def extract_text_from_image(image_bytes: bytes, language: str = "mkd") -> dict:
    processed_image = preprocess_image(image_bytes)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_path = temp_file.name

        Image.fromarray(processed_image).save(temp_path, format="PNG")

        config = "--oem 3 --psm 6"

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
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)