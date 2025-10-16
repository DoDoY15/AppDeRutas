#Import external lib

import pandas as pd
import io
from typing import List

# Import ApI 

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .core import security

from .crud import crud_excel

from .db import models

# Import Local

from dependencies import get_db
from .api.api_v1.endpoints import setup
from .schemas import schemas
from .db.database import SessionLocal, engine

# Create the database table
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title ="API optimizing routes",
    description = "API to manage users and points of sale (POS) for route optimization.",
    version = "1.0.0"
)

# test Root endpoint

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Otimização de Rotas!"}
