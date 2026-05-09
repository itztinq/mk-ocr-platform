from pydantic import BaseModel


class BookPageItem(BaseModel):
    page_number: int
    page_image_path: str
    page_image_url: str
    has_raw: bool
    has_cleaned: bool
    has_corrected: bool


class BookPagesResponse(BaseModel):
    book_name: str
    total_pages: int
    processed_pages: int
    corrected_pages: int
    pages: list[BookPageItem]