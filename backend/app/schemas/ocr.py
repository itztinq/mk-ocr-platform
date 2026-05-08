from pydantic import BaseModel


class OCRResponse(BaseModel):
    filename: str
    content_type: str
    text: str