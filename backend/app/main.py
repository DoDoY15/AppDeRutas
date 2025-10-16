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

# Endpoint para o Admin configurar o sistema com ficheiros Excel

@router.post("/setup", tags=["Admin"])
def setup_system(
    users_file: UploadFile = File(..., description= "Excel file with users data"),
    pos_file: UploadFile = File(..., description= "Excel file with points of sale data"),
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(security.require_admin_user)
):


# Module CRUD to process and load users and points of sale from Excel files

    try:

        users_count = crud_excel.process_and_load_users(db, users_file)
        pos_count = crud_excel.process_and_load_pos(db, pos_file)

        db.commit()

        return {"message": "Setup completed successfully","details": f"{users_count} users and {pos_count} points of sale added."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar o ficheiro de utilizadores: {str(e)}")