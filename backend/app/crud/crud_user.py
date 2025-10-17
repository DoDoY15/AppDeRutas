import io
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.db import models
from ..core import security

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def process_and_load_users(db : Session , file: UploadFile) -> int:

    contents = file.file.read()
    df = pd.read_excel(io.BytesIO(contents))

    for _, row in df.iterrows():
        hashed_password = security.get_password_hash(row['password'])
        db_user = models.User(
            username=row['username'],
            hashed_password=hashed_password,
            role=row['role'])
        db.add(db_user)

    return len(df)


