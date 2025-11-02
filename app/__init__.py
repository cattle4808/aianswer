from fastapi import APIRouter


from .v1.routers import router as v1_router

router = APIRouter()
router.include_router(prefix="/v1", router=v1_router)


from . v1.models import IdScript, CheckRequest

__all__ = ["IdScript", "CheckRequest"]