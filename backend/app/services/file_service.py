from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OCR_OUTPUT_DIR = PROJECT_ROOT / "ocr_output"


def sanitize_stem(filename: str) -> str:
    if not filename:
        return "uploaded-image"

    path = Path(filename)
    stem = path.stem.strip() or "uploaded-image"
    stem = re.sub(r"[^A-Za-z0-9\u0400-\u04FF_-]+", "_", stem)
    return stem


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


def get_output_file(file_type: str, filename: str) -> Path:
    safe_stem = sanitize_stem(filename)

    if file_type == "raw":
        file_path = OCR_OUTPUT_DIR / f"{safe_stem}_raw.txt"
    elif file_type == "cleaned":
        file_path = OCR_OUTPUT_DIR / f"{safe_stem}_cleaned.txt"
    else:
        raise ValueError("Invalid file type. Use 'raw' or 'cleaned'.")

    return file_path