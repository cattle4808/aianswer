from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_",               # DB_URL, DB_TIMEZONE, DB_MEDIA_ROOT
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    url: str
    timezone: str = "Asia/Tashkent"
    media_root: str = "app/storage"
    checks_subdir: str = "check_requests"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",              # APP_DOMAIN, APP_API_DOMAIN, ...
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    domain: str = "http://localhost:8000"
    api_domain: str = "http://localhost:8000"
    script_duration_hours: int = 720    # часы
    script_name_length: int = 3
    script_max_usage: int = 50
    max_key_attempts: int = 20
    max_name_attempts: int = 20

    openai_api_key: str
    permission_keys: list[str] = None

    celery_broker_url: str
    celery_result_backend: str


class ProjectSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PROJECT_",          # PROJECT_DEBUG, PROJECT_NAME, ...
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    debug: bool = True
    name: str = "AI Testing"
    description: str = "AI Testing"
    version: str = "0.0.1"

    @computed_field
    @property
    def docs_url(self) -> str | None:
        return "/docs" if self.debug else None

    @computed_field
    @property
    def redoc_url(self) -> str | None:
        return "/redoc" if self.debug else None

    @computed_field
    @property
    def openapi_url(self) -> str | None:
        return "/openapi.json" if self.debug else None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    db: DBSettings = DBSettings()
    app: AppSettings = AppSettings()
    project: ProjectSettings = ProjectSettings()


settings = Settings()
