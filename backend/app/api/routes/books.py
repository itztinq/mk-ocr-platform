from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.app.schemas.book import BookPagesResponse
from backend.app.schemas.page import BookPageDetailResponse
from backend.app.schemas.page_status import (
    UpdatePageStatusRequest,
    UpdatePageStatusResponse,
)
from backend.app.schemas.text_edit import (
    SaveCorrectedTextRequest,
    SaveCorrectedTextResponse,
)
from backend.app.services.book_service import (
    export_book_text,
    get_book_page,
    get_page_text_file,
    list_book_pages,
    save_corrected_text,
    update_page_status,
)

router = APIRouter(tags=["books"])


@router.get("/books/{book_name}/pages", response_model=BookPagesResponse)
async def get_book_pages(book_name: str) -> BookPagesResponse:
    try:
        data = list_book_pages(book_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return BookPagesResponse(**data)


@router.get("/books/{book_name}/pages/{page_number}", response_model=BookPageDetailResponse)
async def get_single_book_page(book_name: str, page_number: int) -> BookPageDetailResponse:
    try:
        data = get_book_page(book_name, page_number)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return BookPageDetailResponse(**data)


@router.put("/books/{book_name}/pages/{page_number}/corrected-text", response_model=SaveCorrectedTextResponse)
async def update_corrected_text(
    book_name: str,
    page_number: int,
    payload: SaveCorrectedTextRequest,
) -> SaveCorrectedTextResponse:
    try:
        data = save_corrected_text(book_name, page_number, payload.text)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return SaveCorrectedTextResponse(**data)


@router.put("/books/{book_name}/pages/{page_number}/status", response_model=UpdatePageStatusResponse)
async def change_page_status(
    book_name: str,
    page_number: int,
    payload: UpdatePageStatusRequest,
) -> UpdatePageStatusResponse:
    try:
        data = update_page_status(book_name, page_number, payload.status)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UpdatePageStatusResponse(**data)


@router.get("/books/{book_name}/pages/{page_number}/download/{kind}")
async def download_page_text(
    book_name: str,
    page_number: int,
    kind: str,
):
    try:
        file_path = get_page_text_file(book_name, page_number, kind)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return FileResponse(
        path=file_path,
        media_type="text/plain",
        filename=file_path.name,
    )


@router.get("/books/{book_name}/export/txt")
async def download_book_export(book_name: str):
    try:
        export_path = export_book_text(book_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return FileResponse(
        path=export_path,
        media_type="text/plain",
        filename=export_path.name,
    )