from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.meals import router as meals_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import Base, engine

configure_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(meals_router)
app.mount("/uploads", StaticFiles(directory=settings.image_storage_path), name="uploads")


@app.get("/health")
def health_check():
    return {"status": "ok"}
