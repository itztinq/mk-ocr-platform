from fastapi import FastAPI

from backend.app.api.routes.files import router as files_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.ocr import router as ocr_router
from backend.app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(ocr_router)
app.include_router(files_router)