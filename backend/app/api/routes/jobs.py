from fastapi import APIRouter, HTTPException

from backend.app.schemas.job import JobStatusResponse
from backend.app.services.job_service import get_job

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job was not found.")

    return JobStatusResponse(**job)