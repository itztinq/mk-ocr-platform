from copy import deepcopy
from threading import Lock
from uuid import uuid4


JOBS: dict[str, dict] = {}
LOCK = Lock()


def _progress_percent(job: dict) -> float:
    if job["total_files"] == 0:
        return 0.0
    return round((job["processed_files"] / job["total_files"]) * 100, 2)


def _upsert_page(job: dict, filename: str, page_number: int | None, status: str, detail: str | None = None) -> None:
    for page in job["pages"]:
        if page["filename"] == filename:
            page["page_number"] = page_number
            page["status"] = status
            page["detail"] = detail
            return

    job["pages"].append(
        {
            "filename": filename,
            "page_number": page_number,
            "status": status,
            "detail": detail,
        }
    )


def create_job(book_name: str, total_files: int) -> dict:
    job_id = uuid4().hex
    job = {
        "job_id": job_id,
        "book_name": book_name,
        "status": "queued",
        "total_files": total_files,
        "processed_files": 0,
        "successful_files": 0,
        "failed_files": 0,
        "current_page": None,
        "errors": [],
        "pages": [],
    }

    with LOCK:
        JOBS[job_id] = job

    result = deepcopy(job)
    result["progress_percent"] = _progress_percent(result)
    return result


def get_job(job_id: str) -> dict | None:
    with LOCK:
        job = JOBS.get(job_id)
        if not job:
            return None
        result = deepcopy(job)

    result["progress_percent"] = _progress_percent(result)
    return result


def mark_job_running(job_id: str) -> None:
    with LOCK:
        if job_id in JOBS:
            JOBS[job_id]["status"] = "running"


def mark_job_page_started(job_id: str, filename: str, page_number: int | None) -> None:
    with LOCK:
        job = JOBS[job_id]
        job["current_page"] = page_number
        _upsert_page(job, filename, page_number, "running")


def mark_job_page_success(job_id: str, filename: str, page_number: int | None) -> None:
    with LOCK:
        job = JOBS[job_id]
        job["processed_files"] += 1
        job["successful_files"] += 1
        _upsert_page(job, filename, page_number, "completed")


def mark_job_page_failed(job_id: str, filename: str, page_number: int | None, detail: str) -> None:
    with LOCK:
        job = JOBS[job_id]
        job["processed_files"] += 1
        job["failed_files"] += 1
        job["errors"].append(f"{filename}: {detail}")
        _upsert_page(job, filename, page_number, "failed", detail)


def mark_job_completed(job_id: str) -> None:
    with LOCK:
        job = JOBS[job_id]
        job["current_page"] = None
        job["status"] = "completed" if job["failed_files"] == 0 else "completed_with_errors"


def mark_job_failed(job_id: str, detail: str) -> None:
    with LOCK:
        job = JOBS[job_id]
        job["current_page"] = None
        job["status"] = "failed"
        job["errors"].append(detail)