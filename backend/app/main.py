from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.books import router as books_router
from backend.app.api.routes.files import router as files_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.jobs import router as jobs_router
from backend.app.api.routes.ocr import router as ocr_router
from backend.app.api.routes.text import router as text_router
from backend.app.core.config import settings
from backend.app.core.database import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect(
        settings.mongodb_uri,
        settings.mongodb_db_name,
        jobs_collection=settings.mongodb_jobs_collection,
    )

    collection = db.get_jobs_collection()
    await collection.create_index("job_id", unique=True)

    yield

    await db.close()


IMAGES_DIR = settings.images_dir
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(ocr_router)
app.include_router(files_router)
app.include_router(text_router)
app.include_router(jobs_router)
app.include_router(books_router)

app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")
