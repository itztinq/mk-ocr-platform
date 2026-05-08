from fastapi import APIRouter, File, UploadFile

from backend.app.services.ocr_service import process_uploaded_image

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    return await process_uploaded_image(file)