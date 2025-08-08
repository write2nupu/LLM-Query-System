from fastapi import APIRouter

from .v1 import api as v1_api

router = APIRouter(prefix="/api")
router.include_router(v1_api)
