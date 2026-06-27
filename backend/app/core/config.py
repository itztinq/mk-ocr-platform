import os
import sys
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Settings:

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "Macedonian OCR Platform")
        self.app_version: str = os.getenv("APP_VERSION", "0.1.0")
        self.debug: bool = os.getenv("DEBUG", "true").lower() == "true"

        # MongoDB
        self.mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "mk_ocr_platform")
        self.mongodb_jobs_collection: str = os.getenv("MONGODB_JOBS_COLLECTION", "jobs")

        # CORS
        raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
        self.cors_origins: list[str] = [o.strip() for o in raw_origins.split(",") if o.strip()]

        # OCR
        self.ocr_language: str = os.getenv("OCR_LANGUAGE", "mkd")
        _default_tesseract = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if sys.platform == "win32"
            else "/usr/bin/tesseract"
        )
        self.tesseract_cmd: str = os.getenv("TESSERACT_CMD", _default_tesseract)

        # Directory paths
        project_root = Path(
            os.getenv("PROJECT_ROOT", Path(__file__).resolve().parents[3])
        )
        self.project_root: Path = project_root
        self.images_dir: Path = Path(os.getenv("IMAGES_DIR", str(project_root / "images")))
        self.ocr_output_dir: Path = Path(os.getenv("OCR_OUTPUT_DIR", str(project_root / "ocr_output")))
        self.text_output_dir: Path = Path(os.getenv("TEXT_OUTPUT_DIR", str(project_root / "text")))
        self.page_status_dir: Path = Path(
            os.getenv("PAGE_STATUS_DIR", str(project_root / "text_output" / "_status"))
        )


settings = Settings()
