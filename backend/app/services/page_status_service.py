import json
from pathlib import Path
from threading import Lock

from backend.app.services.file_service import PROJECT_ROOT, sanitize_stem

STATUS_DIR = PROJECT_ROOT / "text_output" / "_status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)

LOCK = Lock()
VALID_PAGE_STATUSES = {"pending", "in_review", "done"}


def _status_file(book_name: str) -> Path:
    safe_book_name = sanitize_stem(book_name)
    return STATUS_DIR / f"{safe_book_name}.json"


def _read_status_map(book_name: str) -> dict[str, str]:
    path = _status_file(book_name)
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _write_status_map(book_name: str, data: dict[str, str]) -> None:
    path = _status_file(book_name)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_page_status(book_name: str, page_number: int, has_corrected: bool = False) -> str:
    with LOCK:
        data = _read_status_map(book_name)

    saved_status = data.get(str(page_number))
    if saved_status in VALID_PAGE_STATUSES:
        return saved_status

    return "done" if has_corrected else "pending"


def set_page_status(book_name: str, page_number: int, status: str) -> dict:
    if status not in VALID_PAGE_STATUSES:
        raise ValueError("Invalid page status. Use 'pending', 'in_review', or 'done'.")

    with LOCK:
        data = _read_status_map(book_name)
        data[str(page_number)] = status
        _write_status_map(book_name, data)

    return {
        "book_name": sanitize_stem(book_name),
        "page_number": page_number,
        "status": status,
    }