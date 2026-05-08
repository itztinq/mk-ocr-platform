from fastapi import APIRouter, HTTPException

from backend.app.schemas.text import (
    SaveCorrectedTextRequest,
    SaveCorrectedTextResponse,
)
from backend.app.services.file_service import save_corrected_text

router = APIRouter(prefix="/text", tags=["text"])


@router.post("/save-corrected", response_model=SaveCorrectedTextResponse)
async def save_corrected_text_file(
    payload: SaveCorrectedTextRequest,
) -> SaveCorrectedTextResponse:
    corrected_text = payload.corrected_text.strip()

    if not corrected_text:
        raise HTTPException(
            status_code=400,
            detail="Corrected text cannot be empty."
        )

    saved = save_corrected_text(
        filename=payload.filename,
        corrected_text=corrected_text,
    )

    return SaveCorrectedTextResponse(
        filename=payload.filename,
        saved_path=saved["saved_path"],
        text_length=len(corrected_text),
    )