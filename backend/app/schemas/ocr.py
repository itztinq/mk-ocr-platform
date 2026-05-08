from pydantic import BaseModel


class OCRResponse(BaseModel):
    filename: str
    content_type: str
    language: str
    used_preprocessing: bool
    has_text: bool
    text_length: int
    raw_text: str
    cleaned_text: str
    raw_output_path: str
    cleaned_output_path: str