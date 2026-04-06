from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class LocalImageStorage:
    def __init__(self) -> None:
        self.base_dir = Path(settings.image_storage_path)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file: UploadFile) -> str:
        suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
        filename = f"{uuid4().hex}{suffix}"
        destination = self.base_dir / filename
        with destination.open("wb") as out:
            out.write(file.file.read())
        return str(destination)
