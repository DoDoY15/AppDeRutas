#Import external lib

import pandas as pd
import io
from typing import List

# Import ApI 

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .core import security
from .crud import crud_user, crud_pos
from .db import models

# Import Local

from app.api.api_v1.base import api_router
from .dependencies import get_db
from .api.api_v1.endpoints import upload_setup
from .db.database import SessionLocal, engine

# Create the database table
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title ="API optimizing routes",
    description = "API to manage users and points of sale (POS) for route optimization.",
    version = "1.0.0")

origins = ["http://localhost:3000",
           "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# test Root endpoint

@app.get("/")
def read_root():
    return {"status": "API de Otimização de Rotas está online"}
