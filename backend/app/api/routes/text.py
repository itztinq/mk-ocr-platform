from fastapi import APIRouter, HTTPException

from backend.app.schemas.text import (
    SaveCorrectedTextRequest,
    SaveCorrectedTextResponse,
)
from backend.app.services.file_service import (
    rebuild_book_corrected_output,
    save_corrected_page_text,
)

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

    saved = save_corrected_page_text(
        book_name=payload.book_name,
        page_number=payload.page_number,
        corrected_text=corrected_text,
    )

    book_corrected = rebuild_book_corrected_output(book_name=payload.book_name)

    return SaveCorrectedTextResponse(
        book_name=payload.book_name,
        page_number=payload.page_number,
        saved_path=saved["saved_path"],
        book_corrected_output_path=book_corrected["book_corrected_output_path"],
        text_length=len(corrected_text),
    )