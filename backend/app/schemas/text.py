from pydantic import BaseModel, Field


class SaveCorrectedTextRequest(BaseModel):
    filename: str = Field(..., min_length=1)
    corrected_text: str = Field(..., min_length=1)


class SaveCorrectedTextResponse(BaseModel):
    filename: str
    saved_path: str
    text_length: int