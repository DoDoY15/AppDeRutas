#Import external lib

import pandas as pd
import io
from typing import List

# Import ApI 

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

# Import Local

from . import models, schemas, security
from .database import SessionLocal, engine

# Create the database table
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title ="API optimizing routes",
    description = "API to manage users and points of sale (POS) for route optimization.",
    version = "1.0.0"
)

# Dependencies

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# test Root endpoint

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Otimização de Rotas!"}

# Endpoint para o Admin configurar o sistema com ficheiros Excel

@app.post("/api/admin/setup", tags=["Admin"])
def setup_system(
    users_file: UploadFile = File(..., description= "Excel file with users data"),
    pos_file: UploadFile = File(..., description= "Excel file with points of sale data"),
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(security.require_admin_user)
):
    
    try:

        # clean up existing data
        
        db.query(models.DailyVisit).delete()
        db.query(models.PointOfStop).delete()
        db.query(models.User).delete()
        
        # load and process users file
        
        users_contents = users_file.file.read()
        users_df = pd.read_excel(io.BytesIO(users_contents))

        for _, row in users_df.iterrows():
            hashed_password = security.get_password_hash(row['password'])
            db_user = models.User(
                username=row['username'],
                hashed_password=hashed_password,
                role=row['role'])
            db.add(db_user)
            pos_contents = pos_file.file.read()
            pos_df = pd.read_excel(io.BytesIO(pos_contents))
        
        #translate names of columns if necessary
    
        column_mapping = {
            'ID': 'external_id',
            'Nombre del PDV': 'name',
            'Cadena': 'chain',
            'Segmentación': 'Segment',
            'Canal del PDV': 'channel',
            'Region': 'Region',
            'País': 'country',
            'Ciudad': 'City',
            'Dirección': 'Address',
            'Latitud': 'latitude',
            'Longitud': 'longitude',
            'Activo': 'WorkingStatus',
            'Visitas semanales': 'visits_per_week',
            'Duración visita(horas)': 'visit_duration_hours',
            'Prioridad': 'priority'
        }
        pos_df.rename(columns=column_mapping, inplace=True)
        
        # converrt WorkingStatus to boolean with various possible inputs
        
        pos_df['WorkingStatus'] = pos_df['WorkingStatus'].apply(lambda x: True if str(x).lower() in ['yes', 'true', '1', 'sim' , 'si'] else False)


        for _, row in pos_df.iterrows():
            pos_data_dict = row.to_dict()
            pos_schema = schemas.PointOfStopCreate(**pos_data_dict)
            db_pos = models.PointOfStop(**pos_schema.dict())
            db.add(db_pos) 


        db.commit()
        
        return {"message": "setup completed successfully","details": f"{users_df.shape[0]} users and {pos_df.shape[0]} points of sale added."} 
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar o ficheiro de utilizadores: {str(e)}")