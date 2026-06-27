from datetime import datetime, timezone
from uuid import uuid4

from backend.app.core.database import db


async def create_job(book_name: str, total_files: int) -> dict:
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
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    collection = db.get_jobs_collection()
    await collection.insert_one(job)

    job["progress_percent"] = _progress_percent(job)
    job["_id"] = str(job["_id"])
    return job


async def get_job(job_id: str) -> dict | None:
    collection = db.get_jobs_collection()
    job = await collection.find_one({"job_id": job_id})
    if not job:
        return None

    job["progress_percent"] = _progress_percent(job)
    job["_id"] = str(job["_id"])
    return job


async def mark_job_running(job_id: str) -> None:
    collection = db.get_jobs_collection()
    await collection.update_one(
        {"job_id": job_id},
        {"$set": {"status": "running", "updated_at": datetime.now(timezone.utc)}},
    )


async def mark_job_page_started(job_id: str, filename: str, page_number: int | None) -> None:
    collection = db.get_jobs_collection()

    now = datetime.now(timezone.utc)
    await collection.update_one(
        {"job_id": job_id},
        {"$set": {"current_page": page_number, "updated_at": now}},
    )

    await _upsert_page(job_id, filename, page_number, "running", now)


async def mark_job_page_success(job_id: str, filename: str, page_number: int | None) -> None:
    collection = db.get_jobs_collection()

    now = datetime.now(timezone.utc)
    await collection.update_one(
        {"job_id": job_id},
        {
            "$inc": {"processed_files": 1, "successful_files": 1},
            "$set": {"updated_at": now},
        },
    )

    await _upsert_page(job_id, filename, page_number, "completed", now)


async def mark_job_page_failed(job_id: str, filename: str, page_number: int | None, detail: str) -> None:
    collection = db.get_jobs_collection()

    now = datetime.now(timezone.utc)
    await collection.update_one(
        {"job_id": job_id},
        {
            "$inc": {"processed_files": 1, "failed_files": 1},
            "$push": {"errors": f"{filename}: {detail}"},
            "$set": {"updated_at": now},
        },
    )

    await _upsert_page(job_id, filename, page_number, "failed", detail, now)


async def mark_job_completed(job_id: str) -> None:
    collection = db.get_jobs_collection()

    job = await collection.find_one({"job_id": job_id}, {"failed_files": 1})
    status = "completed" if (job and job.get("failed_files", 0) == 0) else "completed_with_errors"

    await collection.update_one(
        {"job_id": job_id},
        {
            "$set": {
                "status": status,
                "current_page": None,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )


async def mark_job_failed(job_id: str, detail: str) -> None:
    collection = db.get_jobs_collection()

    await collection.update_one(
        {"job_id": job_id},
        {
            "$set": {
                "status": "failed",
                "current_page": None,
                "updated_at": datetime.now(timezone.utc),
            },
            "$push": {"errors": detail},
        },
    )


async def list_jobs(limit: int = 100) -> list[dict]:
    collection = db.get_jobs_collection()
    cursor = collection.find(
        {},
        {
            "job_id": 1,
            "book_name": 1,
            "status": 1,
            "created_at": 1,
            "_id": 0,
        },
    ).sort("created_at", -1).limit(limit)

    return await cursor.to_list(length=limit)


def _progress_percent(job: dict) -> float:
    if job["total_files"] == 0:
        return 0.0
    return round((job["processed_files"] / job["total_files"]) * 100, 2)


async def _upsert_page(
    job_id: str,
    filename: str,
    page_number: int | None,
    status: str,
    updated_at: datetime | None = None,
    detail: str | None = None,
) -> None:
    collection = db.get_jobs_collection()

    result = await collection.update_one(
        {"job_id": job_id, "pages.filename": filename},
        {
            "$set": {
                "pages.$.page_number": page_number,
                "pages.$.status": status,
                "pages.$.detail": detail,
                "updated_at": updated_at or datetime.now(timezone.utc),
            }
        },
    )

    if result.matched_count == 0:
        await collection.update_one(
            {"job_id": job_id},
            {
                "$push": {
                    "pages": {
                        "filename": filename,
                        "page_number": page_number,
                        "status": status,
                        "detail": detail,
                    }
                },
                "$set": {"updated_at": updated_at or datetime.now(timezone.utc)},
            },
        )
