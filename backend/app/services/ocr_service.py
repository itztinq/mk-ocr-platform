from fastapi import HTTPException, UploadFile

from ocr_pipeline.ocr_engine import extract_text_from_image


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
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(exc)}"
        ) from exc

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "text": extracted_text,
    }