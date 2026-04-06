from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Meal Vision MVP"
    environment: str = "development"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24

    database_url: str = "sqlite:///./app.db"

    image_storage_mode: str = "local"
    image_storage_path: str = "uploads"
    max_image_size_mb: int = 8
    allowed_image_types: str = "image/jpeg,image/png,image/webp"

    food_vision_provider: str = "mock"
    nutrition_provider: str = "mock"
    usda_api_key: str | None = None

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_image_types_list(self) -> list[str]:
        return [v.strip() for v in self.allowed_image_types.split(",") if v.strip()]


settings = Settings()
