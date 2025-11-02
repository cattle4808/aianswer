import secrets
import string
import uuid
from typing import Tuple
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from core.config import settings
from . import crud, models, tasks
from app.utils import files



async def __generate_name(
    length: int = 3,
    uppercase: bool = False,
    numbers: bool = False,
) -> str:
    alphabet = string.ascii_lowercase
    if uppercase:
        alphabet += string.ascii_uppercase
    if numbers:
        alphabet += string.digits
    if not alphabet:
        raise ValueError("Alphabet cannot be empty")
    return ''.join(secrets.choice(alphabet) for _ in range(int(length)))


async def __generate_key() -> str:
    return uuid.uuid4().hex


async def create_script(
    db: AsyncSession,
    start_at: datetime | None = None,
    stop_at: datetime | None = None,
    name: str | None = None,
    name_length: int = 3,
) -> models.IdScript:
    if not name:
        name = await __generate_name(length=name_length, uppercase=False, numbers=True)

    if start_at is None:
        start_at = datetime.now(timezone.utc)
    elif start_at.tzinfo is None:
        start_at = start_at.replace(tzinfo=timezone.utc)

    if stop_at is None:
        stop_at = start_at + timedelta(hours=settings.app.script_duration_hours)
    elif stop_at.tzinfo is None:
        stop_at = stop_at.replace(tzinfo=timezone.utc)

    ATTEMPTS = 8
    for _ in range(ATTEMPTS):
        key = await __generate_key()

        try:
            script = await crud.create_script(
                db,
                name=name,
                key=key,
                start_at=start_at,
                stop_at=stop_at,
                status=False,
                max_usage=settings.app.script_max_usage,
                usage=0,
                fingerprint=None,
                script_type="default",
            )
            return script

        except IntegrityError:
            await db.rollback()
            if name is None:
                name = await __generate_name(length=name_length, uppercase=False, numbers=True)
            continue

        except Exception:
            await db.rollback()
            raise

    raise RuntimeError("Failed to create IdScript with unique name/key after several attempts")


async def create_check_request(
    db: AsyncSession,
    script: models.IdScript,
    upload_file,
    dest_subdir: str = "check_requests",
) -> Tuple[bool, str | None]:

    try:
        input_path = await files.stream_save_upload_file(upload_file, dest_subdir=dest_subdir)
    except Exception as e:
        return False, f"save_error: {e!r}"

    last_exc = None
    for attempt in range(settings.app.max_key_attempts):
        key_answer = uuid.uuid4().hex
        try:
            new_req = models.CheckRequest(
                script_id=script.id,
                key_answer=key_answer,
                status="pending",
                input_path=input_path,
                result_json=None,
                error=None,
            )
            db.add(new_req)
            await db.commit()
            await db.refresh(new_req)

            tasks.process_image.apply_async(args=[key_answer], task_id=key_answer, queue="checks")

            return True, key_answer

        except IntegrityError as e:
            await db.rollback()
            last_exc = e
            continue
        except Exception as e:
            await db.rollback()
            return False, f"db_error: {e!r}"

    return False, f"unique_key_failed: {last_exc!r}"

