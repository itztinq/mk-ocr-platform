from fastapi import APIRouter, File, Form, UploadFile

from backend.app.schemas.ocr import OCRResponse
from backend.app.services.ocr_service import process_uploaded_image

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