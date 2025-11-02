import base64
import uuid
from typing import Optional

import aiofiles
from pathlib import Path
from fastapi import UploadFile
from core.config import settings

CHECKS_SUBDIR = "check_requests"


async def stream_save_upload_file(upload_file: UploadFile, dest_subdir: str = CHECKS_SUBDIR) -> str:
    dest_dir = Path(settings.db.media_root) / Path(dest_subdir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    original_ext = Path(upload_file.filename or "").suffix or ".bin"
    filename = f"{uuid.uuid4().hex}{original_ext}"
    out_path = dest_dir / filename

    async with aiofiles.open(out_path, "wb") as out_f:
        while True:
            chunk = await upload_file.read(1024 * 1024)
            if not chunk:
                break
            await out_f.write(chunk)

    return str(Path(dest_subdir) / filename)


def get_file_base64(path: str) -> Optional[str]:
    try:
        with aiofiles.open(path, "rb") as f:
            content = f.read()
            return base64.b64encode(content).decode("utf-8")
    except Exception:
        return None
    
