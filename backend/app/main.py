from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes.files import router as files_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.ocr import router as ocr_router
from backend.app.api.routes.text import router as text_router
from backend.app.core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGES_DIR = PROJECT_ROOT / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(ocr_router)
app.include_router(files_router)
app.include_router(text_router)

app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")