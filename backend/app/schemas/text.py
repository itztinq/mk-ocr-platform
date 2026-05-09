from pydantic import BaseModel, Field


class SaveCorrectedTextRequest(BaseModel):
    book_name: str = Field(..., min_length=1)
    page_number: int = Field(..., ge=1)
    corrected_text: str = Field(..., min_length=1)


class SaveCorrectedTextResponse(BaseModel):
    book_name: str
    page_number: int
    saved_path: str
    book_corrected_output_path: str
    text_length: int