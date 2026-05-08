from fastapi import HTTPException, UploadFile

from backend.app.services.file_service import (
    extract_page_number_from_filename,
    save_page_ocr_outputs,
    save_uploaded_page_image,
)
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


async def process_uploaded_image(
    file: UploadFile,
    book_name: str,
) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload an image."
        )

    if not book_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Book name is required."
        )

    try:
        page_number = extract_page_number_from_filename(file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:
        saved_image = save_uploaded_page_image(
            book_name=book_name,
            page_number=page_number,
            image_bytes=content,
        )

        raw_text = extract_text_from_image(content, language=OCR_LANGUAGE).strip()
        cleaned_text = clean_ocr_text(raw_text).strip()

        saved_outputs = save_page_ocr_outputs(
            book_name=book_name,
            page_number=page_number,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(exc)}"
        ) from exc

    return {
        "filename": file.filename or "uploaded-image",
        "book_name": saved_image["book_name"],
        "page_number": page_number,
        "page_image_path": saved_image["page_image_path"],
        "content_type": file.content_type or "application/octet-stream",
        "language": OCR_LANGUAGE,
        "used_preprocessing": USED_PREPROCESSING,
        "has_text": bool(cleaned_text),
        "text_length": len(cleaned_text),
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "raw_output_path": saved_outputs["raw_output_path"],
        "cleaned_output_path": saved_outputs["cleaned_output_path"],
    }