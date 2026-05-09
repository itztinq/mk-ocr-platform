from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from backend.app.schemas.job import BatchUploadResponse
from backend.app.schemas.ocr import OCRResponse
from backend.app.services.file_service import extract_page_number_from_filename
from backend.app.services.job_service import create_job
from backend.app.services.ocr_service import process_batch_images, process_uploaded_image

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/upload-image", response_model=OCRResponse)
async def upload_image(
    book_name: str = Form(...),
    file: UploadFile = File(...),
) -> OCRResponse:
    result = await process_uploaded_image(
        file=file,
        book_name=book_name,
    )
    return OCRResponse(**result)


@router.post("/batch-upload", response_model=BatchUploadResponse)
async def batch_upload_images(
    background_tasks: BackgroundTasks,
    book_name: str = Form(...),
    files: list[UploadFile] = File(...),
) -> BatchUploadResponse:
    if not book_name.strip():
        raise HTTPException(status_code=400, detail="Book name is required.")

    if not files:
        raise HTTPException(status_code=400, detail="At least one image file is required.")

    prepared_files = []

    for file in files:
        filename = file.filename or ""

        try:
            page_number = extract_page_number_from_filename(filename)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file '{filename}' is empty."
            )

        prepared_files.append(
            {
                "filename": filename,
                "page_number": page_number,
                "content_type": file.content_type,
                "content": content,
            }
        )

    prepared_files.sort(key=lambda item: item["page_number"])

    job = create_job(book_name=book_name, total_files=len(prepared_files))

    background_tasks.add_task(
        process_batch_images,
        job["job_id"],
        book_name,
        prepared_files,
    )

    return BatchUploadResponse(
        job_id=job["job_id"],
        book_name=book_name,
        total_files=len(prepared_files),
        status=job["status"],
    )