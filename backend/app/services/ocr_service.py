from fastapi import HTTPException, UploadFile

from backend.app.services.file_service import (
    extract_page_number_from_filename,
    extract_images_from_pdf,
    rebuild_book_raw_output,
    rebuild_book_cleaned_output,
    save_page_ocr_outputs,
    save_uploaded_page_image,
)
from backend.app.services.job_service import (
    mark_job_completed,
    mark_job_failed,
    mark_job_page_failed,
    mark_job_page_started,
    mark_job_page_success,
    mark_job_running,
)

from ocr_pipeline.ocr_engine import extract_text_from_image


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


async def prepare_pdf_pages(
    file: UploadFile,
    book_name: str,
) -> list[dict]:
    if not book_name.strip():
        raise HTTPException(status_code=400, detail="Book name is required.")

    if (file.content_type or "").lower() not in {"application/pdf"}:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF.")

    pdf_bytes = await file.read()

    try:
        return extract_images_from_pdf(book_name=book_name, pdf_bytes=pdf_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(exc)}") from exc

def process_image_bytes(
    *,
    book_name: str,
    filename: str,
    content_type: str | None,
    image_bytes: bytes,
) -> dict:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Unsupported file type. Please upload an image.")

    if not book_name.strip():
        raise ValueError("Book name is required.")

    page_number = extract_page_number_from_filename(filename)

    if not image_bytes:
        raise ValueError("Uploaded file is empty.")

    saved_image = save_uploaded_page_image(
        book_name=book_name,
        page_number=page_number,
        image_bytes=image_bytes,
        original_filename=filename,
    )

    ocr_result = extract_text_from_image(image_bytes, OCR_LANGUAGE)
    raw_text = ocr_result["raw_text"]
    cleaned_text = ocr_result["cleaned_text"]
    avg_confidence = ocr_result["avg_confidence"]
    suspicious_tokens = ocr_result["suspicious_tokens"]

    saved_outputs = save_page_ocr_outputs(
        book_name=book_name,
        page_number=page_number,
        raw_text=raw_text,
        cleaned_text=cleaned_text,
    )

    book_raw_output = rebuild_book_raw_output(book_name=book_name)
    book_cleaned_output = rebuild_book_cleaned_output(book_name=book_name)

    return {
        "filename": filename or "uploaded-image",
        "book_name": saved_image["book_name"],
        "page_number": page_number,
        "page_image_path": saved_image["page_image_path"],
        "page_image_url": f"/images/{saved_image['book_name']}/{saved_image['page_filename']}",
        "content_type": content_type or "application/octet-stream",
        "language": OCR_LANGUAGE,
        "used_preprocessing": USED_PREPROCESSING,
        "has_text": bool(cleaned_text),
        "text_length": len(cleaned_text),
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "avg_confidence": avg_confidence,
        "suspicious_tokens": suspicious_tokens,
        "raw_output_path": saved_outputs["raw_output_path"],
        "cleaned_output_path": saved_outputs["cleaned_output_path"],
        "book_raw_output_path": book_raw_output["book_raw_output_path"],
        "book_cleaned_output_path": book_cleaned_output["book_cleaned_output_path"],
    }


async def process_uploaded_image(
    file: UploadFile,
    book_name: str,
) -> dict:
    content = await file.read()

    try:
        return process_image_bytes(
            book_name=book_name,
            filename=file.filename or "",
            content_type=file.content_type,
            image_bytes=content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(exc)}"
        ) from exc


def process_batch_images(job_id: str, book_name: str, files_data: list[dict]) -> None:
    mark_job_running(job_id)

    try:
        for item in files_data:
            filename = item["filename"]
            page_number = item["page_number"]

            mark_job_page_started(job_id, filename, page_number)

            try:
                process_image_bytes(
                    book_name=book_name,
                    filename=filename,
                    content_type=item["content_type"],
                    image_bytes=item["content"],
                )
                mark_job_page_success(job_id, filename, page_number)
            except Exception as exc:
                mark_job_page_failed(job_id, filename, page_number, str(exc))

        mark_job_completed(job_id)
    except Exception as exc:
        mark_job_failed(job_id, str(exc))


def process_batch_pdf_pages(job_id: str, book_name: str, pages_data: list[dict]) -> None:
    mark_job_running(job_id)

    try:
        for item in pages_data:
            filename = item["filename"]
            page_number = item["page_number"]

            mark_job_page_started(job_id, filename, page_number)

            try:
                process_image_bytes(
                    book_name=book_name,
                    filename=filename,
                    content_type=item["content_type"],
                    image_bytes=item["content"],
                )
                mark_job_page_success(job_id, filename, page_number)
            except Exception as exc:
                mark_job_page_failed(job_id, filename, page_number, str(exc))

        mark_job_completed(job_id)
    except Exception as exc:
        mark_job_failed(job_id, str(exc))