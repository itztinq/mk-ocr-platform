from pathlib import Path
import io
import re

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[3]
IMAGES_DIR = PROJECT_ROOT / "images"
OCR_OUTPUT_DIR = PROJECT_ROOT / "ocr_output"
TEXT_OUTPUT_DIR = PROJECT_ROOT / "text"


def sanitize_stem(value: str) -> str:
    if not value:
        return "untitled"

    sanitized = re.sub(r"[^A-Za-z0-9\u0400-\u04FF_-]+", "_", value.strip())
    sanitized = sanitized.strip("_")
    return sanitized or "untitled"


def format_page_stem(page_number: int) -> str:
    return f"page_{page_number:03d}"


def extract_page_number_from_filename(filename: str) -> int:
    if not filename:
        raise ValueError("Filename is missing.")

    name = Path(filename).name
    match = re.match(r"^page_(\d{3,})\.(jpg|jpeg|png|webp|bmp|tiff)$", name, re.IGNORECASE)

    if not match:
        raise ValueError(
            "Invalid filename format. Use names like page_001.jpg, page_002.png, etc."
        )

    return int(match.group(1))


def save_uploaded_page_image(book_name: str, page_number: int, image_bytes: bytes) -> dict:
    safe_book_name = sanitize_stem(book_name)
    page_stem = format_page_stem(page_number)

    book_images_dir = IMAGES_DIR / safe_book_name
    book_images_dir.mkdir(parents=True, exist_ok=True)

    image_path = book_images_dir / f"{page_stem}.jpg"

    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(image_path, format="JPEG", quality=95)

    return {
        "book_name": safe_book_name,
        "page_image_path": str(image_path.relative_to(PROJECT_ROOT)),
        "page_filename": image_path.name,
    }


def save_page_ocr_outputs(
    book_name: str,
    page_number: int,
    raw_text: str,
    cleaned_text: str,
) -> dict:
    safe_book_name = sanitize_stem(book_name)
    page_stem = format_page_stem(page_number)

    book_output_dir = OCR_OUTPUT_DIR / safe_book_name / "pages"
    book_output_dir.mkdir(parents=True, exist_ok=True)

    raw_file_path = book_output_dir / f"{page_stem}_raw.txt"
    cleaned_file_path = book_output_dir / f"{page_stem}_cleaned.txt"

    raw_file_path.write_text(raw_text, encoding="utf-8")
    cleaned_file_path.write_text(cleaned_text, encoding="utf-8")

    return {
        "raw_output_path": str(raw_file_path.relative_to(PROJECT_ROOT)),
        "cleaned_output_path": str(cleaned_file_path.relative_to(PROJECT_ROOT)),
    }


def save_corrected_page_text(book_name: str, page_number: int, corrected_text: str) -> dict:
    safe_book_name = sanitize_stem(book_name)
    page_stem = format_page_stem(page_number)

    book_text_dir = TEXT_OUTPUT_DIR / safe_book_name / "pages"
    book_text_dir.mkdir(parents=True, exist_ok=True)

    corrected_file_path = book_text_dir / f"{page_stem}_corrected.txt"
    corrected_file_path.write_text(corrected_text, encoding="utf-8")

    return {
        "saved_path": str(corrected_file_path.relative_to(PROJECT_ROOT)),
    }


def _read_page_files_sorted(directory: Path, suffix: str) -> list[str]:
    if not directory.exists():
        return []

    files = sorted(directory.glob(f"page_*{suffix}"))
    contents = []

    for file_path in files:
        text = file_path.read_text(encoding="utf-8").strip()
        if text:
            contents.append(text)

    return contents


def rebuild_book_raw_output(book_name: str) -> dict:
    safe_book_name = sanitize_stem(book_name)

    pages_dir = OCR_OUTPUT_DIR / safe_book_name / "pages"
    final_file_path = OCR_OUTPUT_DIR / f"{safe_book_name}_ocr_raw.txt"

    page_texts = _read_page_files_sorted(pages_dir, "_raw.txt")
    combined_text = "\n\n".join(page_texts).strip()

    final_file_path.write_text(combined_text, encoding="utf-8")

    return {
        "book_raw_output_path": str(final_file_path.relative_to(PROJECT_ROOT)),
    }


def rebuild_book_corrected_output(book_name: str) -> dict:
    safe_book_name = sanitize_stem(book_name)

    pages_dir = TEXT_OUTPUT_DIR / safe_book_name / "pages"
    final_file_path = TEXT_OUTPUT_DIR / f"{safe_book_name}_corrected.txt"

    page_texts = _read_page_files_sorted(pages_dir, "_corrected.txt")
    combined_text = "\n\n".join(page_texts).strip()

    final_file_path.write_text(combined_text, encoding="utf-8")

    return {
        "book_corrected_output_path": str(final_file_path.relative_to(PROJECT_ROOT)),
    }


def save_ocr_outputs(filename: str, raw_text: str, cleaned_text: str) -> dict:
    OCR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    safe_stem = sanitize_stem(filename)

    raw_file_path = OCR_OUTPUT_DIR / f"{safe_stem}_raw.txt"
    cleaned_file_path = OCR_OUTPUT_DIR / f"{safe_stem}_cleaned.txt"

    raw_file_path.write_text(raw_text, encoding="utf-8")
    cleaned_file_path.write_text(cleaned_text, encoding="utf-8")

    return {
        "raw_output_path": str(raw_file_path.relative_to(PROJECT_ROOT)),
        "cleaned_output_path": str(cleaned_file_path.relative_to(PROJECT_ROOT)),
    }


def save_corrected_text(filename: str, corrected_text: str) -> dict:
    TEXT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    safe_stem = sanitize_stem(filename)
    corrected_file_path = TEXT_OUTPUT_DIR / f"{safe_stem}_corrected.txt"

    corrected_file_path.write_text(corrected_text, encoding="utf-8")

    return {
        "saved_path": str(corrected_file_path.relative_to(PROJECT_ROOT)),
    }


def get_output_file(file_type: str, filename: str) -> Path:
    safe_stem = sanitize_stem(filename)

    if file_type == "raw":
        file_path = OCR_OUTPUT_DIR / f"{safe_stem}_raw.txt"
    elif file_type == "cleaned":
        file_path = OCR_OUTPUT_DIR / f"{safe_stem}_cleaned.txt"
    elif file_type == "corrected":
        file_path = TEXT_OUTPUT_DIR / f"{safe_stem}_corrected.txt"
    else:
        raise ValueError("Invalid file type. Use 'raw', 'cleaned' or 'corrected'.")

    return file_path

def get_book_output_file(file_type: str, book_name: str) -> Path:
    safe_book_name = sanitize_stem(book_name)

    if file_type == "raw":
        file_path = OCR_OUTPUT_DIR / f"{safe_book_name}_ocr_raw.txt"
    elif file_type == "corrected":
        file_path = TEXT_OUTPUT_DIR / f"{safe_book_name}_corrected.txt"
    else:
        raise ValueError("Invalid book file type. Use 'raw' or 'corrected'.")

    return file_path