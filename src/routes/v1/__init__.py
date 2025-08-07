from fastapi import APIRouter

from .webhook import router as webhook_router

api = APIRouter(prefix="/v1")
api.include_router(webhook_router)
