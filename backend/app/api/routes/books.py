from fastapi import APIRouter, HTTPException

from backend.app.schemas.book import BookPagesResponse
from backend.app.services.book_service import list_book_pages

router = APIRouter(tags=["books"])


@router.get("/books/{book_name}/pages", response_model=BookPagesResponse)
async def get_book_pages(book_name: str) -> BookPagesResponse:
    try:
        data = list_book_pages(book_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return BookPagesResponse(**data)