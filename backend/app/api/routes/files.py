from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.services.file_service import get_output_file

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/download/{file_type}/{filename}")
async def download_output_file(file_type: str, filename: str):
    try:
        file_path = get_output_file(file_type=file_type, filename=filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Requested file was not found.")

    return FileResponse(
        path=file_path,
        media_type="text/plain",
        filename=file_path.name,
    )