from fastapi import APIRouter

from .endpoints import login
from .endpoints import optimizer
from .endpoints import upload_setup 

api_router = APIRouter()

api_router.include_router(login.router, tags=["authentication"])

api_router.include_router(
    optimizer.router, 
    prefix="/optimize", 
    tags=["optimizer"]
)

api_router.include_router(
    upload_setup.router, 
    prefix="/setup", 
    tags=["upload_setup"]
)