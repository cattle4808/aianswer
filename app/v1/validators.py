from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models


async def check_usage(db: AsyncSession, script: models.IdScript) -> (bool, str):
    stmt = (
        select(models.IdScript.usage, models.IdScript.max_usage)
        .where(models.IdScript.key == script.key)
        .limit(1)
    )

    res = await db.execute(stmt)
    row = res.first()

    if not row:
        return False, "not_found"

    usage, max_usage = row

    if usage >= max_usage:
        return False, "max_usage"

    return True, "ok"

async def check_fingerprint(db: AsyncSession, key: str, fingerprint: str) -> tuple[bool, str]:
    stmt = (
        select(models.IdScript.fingerprint)
        .where(models.IdScript.key == key)
        .limit(1)
    )
    res = await db.execute(stmt)
    row = res.first()

    if not row:
        return True, "not_found"

    db_fingerprint = row[0]

    if db_fingerprint is None:
        return True, "not_found"

    if db_fingerprint != fingerprint:
        return False, "incorrect_fingerprint"

    return True, "ok"


async def check_time_difference_start_and_stop(
    db: AsyncSession, script: models.IdScript
) -> tuple[bool, str]:
    start = script.start_at
    stop = script.stop_at
    now = datetime.now(timezone.utc)

    if start and start > now:
        return False, "script not started yet"

    if stop and now > stop:
        return False, "script expired"

    return True, "ok"


