from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    String, Boolean, DateTime, Integer, Text, ForeignKey, text,
    CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from core.db import Base


class IdScript(Base):
    __tablename__ = "id_scripts"

    # первичные уникальные данные
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # доступ/статус
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    fingerprint: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # расписание (UTC)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    stop_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # лимиты/счётчики
    max_usage: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("50"))
    usage:     Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    # тип скрипта
    script_type: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("'default'"))

    # метаданные (UTC)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    requests: Mapped[list["CheckRequest"]] = relationship(
        back_populates="script",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="desc(CheckRequest.created_at)",
    )

    # __table_args__ = (
    #     CheckConstraint("usage >= 0", name="ck_id_scripts_usage_nonneg"),
    #     CheckConstraint("max_usage >= 0", name="ck_id_scripts_max_usage_nonneg"),
    #     CheckConstraint(
    #         "start_at IS NULL OR stop_at IS NULL OR start_at <= stop_at",
    #         name="ck_id_scripts_time_window",
    #     ),
    #     Index("ix_id_scripts_status_window", "status", "start_at", "stop_at"),
    # )

    def __repr__(self) -> str:  # для логов удобно
        return f"IdScript(id={self.id!r}, key={self.key!r}, name={self.name!r}, status={self.status!r})"


class CheckRequest(Base):
    __tablename__ = "check_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    script_id: Mapped[int] = mapped_column(
        ForeignKey("id_scripts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    key_answer: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)

    # pending|processing|done|error
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'pending'"))

    # путь к принятому входному файлу/изображению
    input_path: Mapped[str] = mapped_column(String(512), nullable=False)

    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    script: Mapped["IdScript"] = relationship(
        back_populates="requests",
        lazy="joined",
    )

    # __table_args__ = (
    #     Index("ix_check_requests_script_created", "script_id", "created_at"),
    #     CheckConstraint(
    #         "status IN ('pending','processing','done','error')",
    #         name="ck_check_requests_status",
    #     ),
    # )

    def __repr__(self) -> str:
        return f"CheckRequest(id={self.id!r}, key_answer={self.key_answer!r}, status={self.status!r})"
