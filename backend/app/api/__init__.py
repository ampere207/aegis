from fastapi import APIRouter

router = APIRouter()

from . import store_token

router.include_router(store_token.router, prefix="/auth", tags=["auth"]) 
