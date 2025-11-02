from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_db
from . import schemas
from . import services
from . import crud
from . import validators

router = APIRouter()

@router.get("/get_script_by_name", response_model=schemas.GetScriptByNameOrKey, tags=["Get info for script"])
async def get_script_by_name(
        name: str,
        db: AsyncSession = Depends(get_db)
    ):
    script = await crud.get_script_by_name(db, name)

    if not script:
        raise StarletteHTTPException(status_code=404)

    return schemas.GetScriptByNameOrKey.model_validate(script).model_dump()

@router.get("/get_script_by_key", response_model=schemas.GetScriptByNameOrKey, tags=["Get info for script"])
async def get_script_by_key(
        key: str,
        db: AsyncSession = Depends(get_db)
    ):
    script = await crud.get_script_by_key(db, key)

    if not script:
        raise StarletteHTTPException(status_code=400)

    return schemas.GetScriptByNameOrKey.model_validate(script).model_dump()


@router.post("/create_script", response_model=schemas.ApiResponse, tags=["Create script"])
async def create_script(
    payload: schemas.GenerateScriptIn,
    db: AsyncSession = Depends(get_db),
    ):
    payload_dict = payload.model_dump(exclude_none=True)
    script = await services.create_script(db, **payload_dict)

    return schemas.ApiResponse(data=schemas.GenerateScriptOut.model_validate(script).model_dump())


@router.post("/check", tags=["Answer check"])
async def check_answer(
        key: str,
        fingerprint: str,
        image: UploadFile = File(..., description="image/*"),
        db: AsyncSession = Depends(get_db)
    ):
    script = await crud.get_script_by_key(db, key)

    valid_fingerprint = await validators.check_fingerprint(db, key, fingerprint)

    if not valid_fingerprint[0]:
        raise StarletteHTTPException(status_code=400)

    if valid_fingerprint[1] == "not_found":
        script = await crud.update_fingerprint(db, key, fingerprint)

    if not script:
        raise StarletteHTTPException(status_code=400)

    usage = await validators.check_usage(db, script)
    if not usage[0]:
        raise StarletteHTTPException(status_code=400)

    usage = await crud.update_usage(db, key, usage=1)
    if not usage:
        raise StarletteHTTPException(status_code=400)

    ok, payload = await services.create_check_request(db, script, image, settings.db.checks_subdir)
    if not ok:
        if str(payload).startswith("save_error"):
            return JSONResponse(status_code=400, content={"ok": False, "error": payload})
        return JSONResponse(status_code=500, content={"ok": False, "error": payload})

    key_answer = payload
    return JSONResponse(status_code=200, content={"ok": True, "data": {"key_answer": key_answer}})

@router.get("/check", response_model=schemas.GetAnswerOut, tags=["Answer check"])
async def get_answer(
        key_answer: str,
        db: AsyncSession = Depends(get_db)
    ):
    answer = await crud.get_answer(db, key_answer)

    if not answer:
        raise StarletteHTTPException(status_code=400)

    return schemas.GetAnswerOut.model_validate(answer).model_dump()





