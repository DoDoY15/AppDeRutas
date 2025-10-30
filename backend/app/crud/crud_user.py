import io
import pandas as pd
import numpy as np 
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.db import models
from ..core import security
from ..schemas.user import UserCreate 

DEFAULT_PASSWORD = "123456"

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user

def process_and_load_users(db: Session, users_file: UploadFile) -> int:
    
    users_file.file.seek(0)
    contents = users_file.file.read()
    df = pd.read_excel(io.BytesIO(contents))
    df = df.astype(object).where(pd.notnull(df), None) 

    column_mapping = {
        'Usuario': 'username',
        'Perfil de acceso': 'role',
        'Latitud': 'start_latitude',
        'Longitud': 'start_longitude',
        'Horas por día usuario': 'daily_work_duration_hours', 
        'Visitas maximas por dia': 'max_visits_per_day',
        'E-mail': 'email', 
        'Nombre del empleado': 'full_name'
    }
    df.rename(columns=column_mapping, inplace=True)

    if 'daily_work_duration_hours' in df.columns:
        df['daily_work_duration_seconds'] = df['daily_work_duration_hours'].apply(
            lambda x: int(x * 3600) if x is not None else None
        )
    else: df['daily_work_duration_seconds'] = 28800 

    if 'role' in df.columns:
        df['role'] = df['role'].apply(
            lambda x: 'admin' if str(x).lower() == 'admin' else 'user'
        )
    else: df['role'] = 'user'

    users_data_list = df.to_dict('records')
    objects_to_add = []
    schema_keys = set(UserCreate.model_fields.keys())

    for user_data in users_data_list:
        schema_data = {
            key: user_data[key] for key in user_data 
            if key in schema_keys and user_data[key] is not None
        }
        schema_data['password'] = DEFAULT_PASSWORD

        try:
            user_schema = UserCreate(**schema_data) 
        except Exception as e:
            print(f"Erro ao validar Usuário: {e} - Dados: {schema_data}")
            continue

        password_str = str(user_schema.password)

        password_to_hash = password_str.encode('utf-8')[:72] 

        hashed_password = security.get_password_hash(password_to_hash.decode('utf-8'))
        user_model_data = user_schema.dict(exclude={'password'}) 
        
        db_user = models.User(
            **user_model_data,
            hashed_password=hashed_password
        )
        objects_to_add.append(db_user)

    db.add_all(objects_to_add)
    return len(objects_to_add)

