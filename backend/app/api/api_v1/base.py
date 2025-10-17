from fastapi import APIRouter
from .endpoints import login, upload_setup

api_router = APIRouter()

api_router.include_router(login.router, tags=["authentication"])
api_router.include_router(upload_setup.router, prefix="/setup", tags=["upload_setup"])        

