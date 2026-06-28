from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.job import JobHistoryResponse, JobStatusResponse
from backend.app.services.job_service import delete_all_jobs, delete_job, get_job, list_jobs

router = APIRouter(tags=["jobs"])


@router.get("/jobs/history", response_model=JobHistoryResponse)
async def get_job_history(limit: int = Query(100, ge=1, le=500)) -> JobHistoryResponse:
    jobs = await list_jobs(limit=limit)
    return JobHistoryResponse(jobs=jobs)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    job = await get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job was not found.")

    return JobStatusResponse(**job)


@router.delete("/jobs/history")
async def clear_job_history() -> dict:
    deleted = await delete_all_jobs()
    return {"deleted": deleted}


@router.delete("/jobs/{job_id}")
async def remove_job(job_id: str) -> dict:
    deleted = await delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job was not found.")
    return {"deleted": True}
