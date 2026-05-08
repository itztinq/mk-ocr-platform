from fastapi import HTTPException, UploadFile

from ocr_pipeline.ocr_engine import extract_text_from_image
from ocr_pipeline.text_cleaner import clean_ocr_text


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
}

OCR_LANGUAGE = "mkd"
USED_PREPROCESSING = True


async def process_uploaded_image(file: UploadFile) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload an image."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:
        raw_text = extract_text_from_image(content, language=OCR_LANGUAGE)
        cleaned_text = clean_ocr_text(raw_text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(exc)}"
        ) from exc

    cleaned_text = cleaned_text.strip()
    raw_text = raw_text.strip()

    return {
        "filename": file.filename or "uploaded-image",
        "content_type": file.content_type or "application/octet-stream",
        "language": OCR_LANGUAGE,
        "used_preprocessing": USED_PREPROCESSING,
        "has_text": bool(cleaned_text),
        "text_length": len(cleaned_text),
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
    }