from pydantic import BaseModel, Field


class SaveCorrectedTextRequest(BaseModel):
    text: str = Field(..., description="Final corrected text for the page.")


class SaveCorrectedTextResponse(BaseModel):
    book_name: str
    page_number: int
    corrected_text_path: str
    saved_characters: int
    status: str