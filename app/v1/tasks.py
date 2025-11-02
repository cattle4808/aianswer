from celery import shared_task
import asyncio
import aiofiles
import base64
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings
from . import crud
from app.utils import image2text

MEDIA_DIR = Path(settings.db.media_root)

@shared_task(bind=True, name="tasks.process_image", soft_time_limit=500, time_limit=1000)
def process_image(self, key_answer: str):
    async def _inner():
        engine = create_async_engine(settings.db.url, future=True)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        try:
            async with AsyncSessionLocal() as db:
                answer = await crud.get_answer(db, key_answer)
                if not answer:
                    return {"ok": False, "error": "not_found"}

                path = MEDIA_DIR / Path(answer.input_path)
                if not path.exists():
                    await crud.update_answer(db, key_answer, status="failed", error="file_not_found")
                    return {"ok": False, "error": "file_not_found"}

                try:
                    async with aiofiles.open(path, "rb") as f:
                        content = await f.read()
                    image_b64 = base64.b64encode(content).decode("utf-8")
                except Exception:
                    await crud.update_answer(db, key_answer, status="failed", error="read_error")
                    return {"ok": False, "error": "read_error"}

                try:
                    text = await asyncio.to_thread(image2text.solve_task, image_b64)
                except Exception as e:
                    await crud.update_answer(db, key_answer, status="failed", error=repr(e))
                    return {"ok": False, "error": "ai_failed"}

                await crud.update_answer(db, key_answer, result_json={"text": text}, status="completed")
                return {"ok": True, "question": text}
        finally:
            await engine.dispose()

    return asyncio.run(_inner())
