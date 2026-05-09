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


def list_book_pages(book_name: str) -> dict:
    safe_book_name = sanitize_stem(book_name)
    book_images_dir = IMAGES_DIR / safe_book_name

    if not book_images_dir.exists() or not book_images_dir.is_dir():
        raise FileNotFoundError("Book images directory was not found.")

    image_files = sorted(book_images_dir.glob("page_*.*"))
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