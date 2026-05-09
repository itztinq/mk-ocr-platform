from pathlib import Path

from backend.app.services.file_service import (
    IMAGES_DIR,
    OCR_OUTPUT_DIR,
    PROJECT_ROOT,
    TEXT_OUTPUT_DIR,
    extract_page_number_from_filename,
    format_page_stem,
    sanitize_stem,
)


def _read_text_file(path: Path) -> dict:
    if not path.exists():
        return {
            "exists": False,
            "path": None,
            "content": None,
        }

    return {
        "exists": True,
        "path": path.relative_to(PROJECT_ROOT).as_posix(),
        "content": path.read_text(encoding="utf-8"),
    }


def list_book_pages(book_name: str) -> dict:
    safe_book_name = sanitize_stem(book_name)
    book_images_dir = IMAGES_DIR / safe_book_name

    if not book_images_dir.exists() or not book_images_dir.is_dir():
        raise FileNotFoundError("Book images directory was not found.")

    image_files = sorted(
        book_images_dir.glob("page_*.*"),
        key=lambda path: extract_page_number_from_filename(path.name),
    )

    pages = []

    for image_path in image_files:
        page_number = extract_page_number_from_filename(image_path.name)
        page_stem = format_page_stem(page_number)

        raw_path = OCR_OUTPUT_DIR / safe_book_name / "pages" / f"{page_stem}_raw.txt"
        cleaned_path = OCR_OUTPUT_DIR / safe_book_name / "pages" / f"{page_stem}_cleaned.txt"
        corrected_path = TEXT_OUTPUT_DIR / safe_book_name / "pages" / f"{page_stem}_corrected.txt"

        pages.append(
            {
                "page_number": page_number,
                "page_image_path": image_path.relative_to(PROJECT_ROOT).as_posix(),
                "page_image_url": f"/images/{safe_book_name}/{image_path.name}",
                "has_raw": raw_path.exists(),
                "has_cleaned": cleaned_path.exists(),
                "has_corrected": corrected_path.exists(),
            }
        )

    processed_pages = sum(1 for page in pages if page["has_raw"])
    corrected_pages = sum(1 for page in pages if page["has_corrected"])

    return {
        "book_name": safe_book_name,
        "total_pages": len(pages),
        "processed_pages": processed_pages,
        "corrected_pages": corrected_pages,
        "pages": pages,
    }


def get_book_page(book_name: str, page_number: int) -> dict:
    safe_book_name = sanitize_stem(book_name)
    page_stem = format_page_stem(page_number)

    book_images_dir = IMAGES_DIR / safe_book_name
    image_candidates = sorted(book_images_dir.glob(f"{page_stem}.*"))

    if not image_candidates:
        raise FileNotFoundError("Page image was not found.")

    image_path = image_candidates[0]

    raw_path = OCR_OUTPUT_DIR / safe_book_name / "pages" / f"{page_stem}_raw.txt"
    cleaned_path = OCR_OUTPUT_DIR / safe_book_name / "pages" / f"{page_stem}_cleaned.txt"
    corrected_path = TEXT_OUTPUT_DIR / safe_book_name / "pages" / f"{page_stem}_corrected.txt"

    return {
        "book_name": safe_book_name,
        "page_number": page_number,
        "page_image_path": image_path.relative_to(PROJECT_ROOT).as_posix(),
        "page_image_url": f"/images/{safe_book_name}/{image_path.name}",
        "raw_text": _read_text_file(raw_path),
        "cleaned_text": _read_text_file(cleaned_path),
        "corrected_text": _read_text_file(corrected_path),
    }


def save_corrected_text(book_name: str, page_number: int, text: str) -> dict:
    safe_book_name = sanitize_stem(book_name)
    page_stem = format_page_stem(page_number)

    book_images_dir = IMAGES_DIR / safe_book_name
    image_candidates = sorted(book_images_dir.glob(f"{page_stem}.*"))

    if not image_candidates:
        raise FileNotFoundError("Page image was not found.")

    corrected_dir = TEXT_OUTPUT_DIR / safe_book_name / "pages"
    corrected_dir.mkdir(parents=True, exist_ok=True)

    corrected_path = corrected_dir / f"{page_stem}_corrected.txt"
    corrected_path.write_text(text, encoding="utf-8")

    return {
        "book_name": safe_book_name,
        "page_number": page_number,
        "corrected_text_path": corrected_path.relative_to(PROJECT_ROOT).as_posix(),
        "saved_characters": len(text),
        "status": "saved",
    }


def get_page_text_file(book_name: str, page_number: int, kind: str) -> Path:
    safe_book_name = sanitize_stem(book_name)
    page_stem = format_page_stem(page_number)

    candidates = {
        "raw": OCR_OUTPUT_DIR / safe_book_name / "pages" / f"{page_stem}_raw.txt",
        "cleaned": OCR_OUTPUT_DIR / safe_book_name / "pages" / f"{page_stem}_cleaned.txt",
        "corrected": TEXT_OUTPUT_DIR / safe_book_name / "pages" / f"{page_stem}_corrected.txt",
    }

    if kind not in candidates:
        raise ValueError("Invalid text kind. Use 'raw', 'cleaned', or 'corrected'.")

    path = candidates[kind]

    if not path.exists():
        raise FileNotFoundError(f"{kind.capitalize()} text file was not found.")

    return path