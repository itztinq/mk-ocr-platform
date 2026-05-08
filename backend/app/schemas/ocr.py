from pydantic import BaseModel


class OCRResponse(BaseModel):
    filename: str
    book_name: str
    page_number: int
    page_image_path: str
    content_type: str
    language: str
    used_preprocessing: bool
    has_text: bool
    text_length: int
    raw_text: str
    cleaned_text: str
    raw_output_path: str
    cleaned_output_path: str