from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional


from . import models


async def get_script_by_key(db: AsyncSession, key: str) -> models.IdScript | None:
    res = await db.execute(
        select(models.IdScript).where(models.IdScript.key == key).limit(1)
    )
    return res.scalar_one_or_none()


async def get_script_by_name(db: AsyncSession, name: str) -> models.IdScript | None:
    res = await db.execute(
        select(models.IdScript).where(models.IdScript.name == name).limit(1)
    )
    return res.scalar_one_or_none()


async def create_script(
    db: AsyncSession,
    *,
    name: str,
    key: str,
    start_at: Optional[datetime] = None,
    stop_at: Optional[datetime] = None,
    status: bool = False,
    max_usage: int = 75,
    usage: int = 0,
    fingerprint: Optional[str] = None,
    script_type: str = "default",
) -> models.IdScript:

    if start_at and start_at.tzinfo is None:
        start_at = start_at.replace(tzinfo=timezone.utc)
    if stop_at and stop_at.tzinfo is None:
        stop_at = stop_at.replace(tzinfo=timezone.utc)

    script = models.IdScript(
        name=name,
        key=key,
        start_at=start_at,
        stop_at=stop_at,
        status=status,
        max_usage=max_usage,
        usage=usage,
        fingerprint=fingerprint,
        script_type=script_type,
    )
    db.add(script)
    try:
        await db.commit()
        await db.refresh(script)
        return script
    except:
        await db.rollback()
        raise


async def update_fingerprint(db: AsyncSession, key: str, fingerprint: str) -> models.IdScript | None:
    stmt = (
        update(models.IdScript)
        .where(models.IdScript.key == key)
        .values(fingerprint=fingerprint)
        .returning(models.IdScript)
    )
    result = await db.execute(stmt)
    await db.commit()

    return result.scalar_one_or_none()

async def update_usage(db: AsyncSession, key: str, usage: int = 1) -> models.IdScript | None:
    stmt = (
        update(models.IdScript)
        .where(models.IdScript.key == key)
        .values(usage=models.IdScript.usage + usage)
        .returning(models.IdScript)
    )
    result = await db.execute(stmt)
    await db.commit()

    return result.scalar_one_or_none()

async def get_answer(db: AsyncSession, key_answer: str) -> models.CheckRequest | None:
    stmt = (
        select(models.CheckRequest)
        .where(models.CheckRequest.key_answer == key_answer)
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_answer(db: AsyncSession, key_answer: str, **kwargs) -> models.CheckRequest | None:
    stmt = (
        update(models.CheckRequest)
        .where(models.CheckRequest.key_answer == key_answer)
        .values(**kwargs)
        .returning(models.CheckRequest)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()