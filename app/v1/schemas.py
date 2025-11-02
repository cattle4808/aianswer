from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime

from sqlalchemy import NullPool


class ApiResponse(BaseModel):
    ok: bool = True
    data: dict | None = None
    error: Optional[str] = None


class DBConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str = Field(..., description="SQLAlchemy DB URL (может быть замаскирован)")
    timezone: str = Field(..., description="Часовой пояс приложения/БД")
    media_root: str = Field(..., description="Путь для медиа-файлов")


class AppConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    domain: str = Field(..., description="Публичный домен фронта/сайта")
    api_domain: str = Field(..., description="Базовый домен API")
    script_duration_hours: int = Field(..., description="Время жизни скрипта (часы)")
    script_name_length: int = Field(..., description="Мин. длина имени скрипта")
    script_max_usage: int = Field(..., description="Лимит использований скрипта")


class ProjectConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    debug: bool = Field(..., description="DEBUG флаг")
    name: str = Field(..., description="Название проекта")
    description: str = Field(..., description="Описание проекта")
    version: str = Field(..., description="Версия проекта")
    docs_url: Optional[str] = Field(None, description="Путь к Swagger UI")
    redoc_url: Optional[str] = Field(None, description="Путь к ReDoc")
    openapi_url: Optional[str] = Field(None, description="Путь к OpenAPI JSON")


class SettingsOut(BaseModel):
    project: ProjectConfig
    app: AppConfig
    db: DBConfig


class GenerateScriptIn(BaseModel):
    start_at: Optional[datetime] = Field(default=None)
    stop_at: Optional[datetime] = Field(default=None)
    name_length: Optional[int] = Field(default=3, ge=3, le=32)


class GenerateScriptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    name: str
    status: bool
    usage: int
    max_usage: int
    script_type: str
    start_at: Optional[datetime] = None
    stop_at: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GetScriptByNameOrKey(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    name: str
    status: bool
    usage: int
    max_usage: int
    key: str
    name: str
    status: bool
    fingerprint: Optional[str] = None
    usage: int
    max_usage: int
    script_type: str
    start_at: Optional[datetime] = None
    stop_at: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GetAnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    script_id: int
    key_answer: str
    status: str
    input_path: Optional[str] = None
    result_json: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


