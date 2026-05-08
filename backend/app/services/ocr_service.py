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
        extracted_text = extract_text_from_image(content, language="mkd")
        cleaned_text = clean_ocr_text(extracted_text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(exc)}"
        ) from exc

    return {
        "filename": file.filename or "uploaded-image",
        "content_type": file.content_type or "application/octet-stream",
        "text": cleaned_text,
    }