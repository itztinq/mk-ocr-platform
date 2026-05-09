from typing import Literal

from pydantic import BaseModel


class UpdatePageStatusRequest(BaseModel):
    status: Literal["pending", "in_review", "done"]


class UpdatePageStatusResponse(BaseModel):
    book_name: str
    page_number: int
    status: Literal["pending", "in_review", "done"]