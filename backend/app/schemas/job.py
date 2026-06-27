from datetime import datetime

from pydantic import BaseModel


class BatchUploadResponse(BaseModel):
    job_id: str
    book_name: str
    total_files: int
    status: str


class JobHistoryItem(BaseModel):
    job_id: str
    book_name: str
    status: str
    created_at: datetime


class JobHistoryResponse(BaseModel):
    jobs: list[JobHistoryItem]


class JobPageStatus(BaseModel):
    filename: str
    page_number: int | None = None
    status: str
    detail: str | None = None


class JobStatusResponse(BaseModel):
    job_id: str
    book_name: str
    status: str
    total_files: int
    processed_files: int
    successful_files: int
    failed_files: int
    progress_percent: float
    current_page: int | None = None
    errors: list[str]
    pages: list[JobPageStatus]