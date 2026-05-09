from pydantic import BaseModel


class PageTextBlock(BaseModel):
    exists: bool
    path: str | None = None
    content: str | None = None


class BookPageDetailResponse(BaseModel):
    book_name: str
    page_number: int
    page_image_path: str
    page_image_url: str
    raw_text: PageTextBlock
    cleaned_text: PageTextBlock
    corrected_text: PageTextBlock