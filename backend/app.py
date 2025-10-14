from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from . import models, schemas, security
from typing import List
from .database import SessionLocal, engine
import pandas as pd
import io

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title ="API optimizacion de rutas")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Otimização de Rotas!"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from . import models, schemas, security
from .database import SessionLocal, engine


# Endpoint para o Admin configurar o sistema com ficheiros Excel
@app.post("/api/admin/setup", tags=["Admin"])
def setup_system(
    users_file: UploadFile = File(...),
    pos_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # A LINHA CORRIGIDA ESTÁ AQUI
    current_admin: schemas.User = Depends(security.require_admin_user)
):
    """
    Recebe dois ficheiros Excel e popula o banco de dados.
    - **users_file**: Excel com colunas 'username', 'password', 'role'
    - **pos_file**: Excel com colunas 'name', 'latitude', 'longitude', 'required_visits_per_week'
    """
    try:
        # --- Processa o ficheiro de utilizadores ---
        users_contents = users_file.file.read()
        users_df = pd.read_excel(io.BytesIO(users_contents))

        # Validação básica de colunas
        required_user_cols = {'username', 'password', 'role'}
        if not required_user_cols.issubset(users_df.columns):
            raise HTTPException(status_code=400, detail="Ficheiro de utilizadores com colunas em falta.")

        for index, row in users_df.iterrows():
            # Aqui vamos adicionar a lógica para criar o utilizador no banco
            # Por agora, vamos apenas imprimir para testar
            print(f"A criar utilizador: {row['username']}")
            # OBS: Em um projeto real, a senha deve ser 'hasheada' antes de salvar!
            # Por simplicidade, vamos ignorar o hashing por enquanto.
            user_data = schemas.UserCreate(
                username=row['username'],
                password=row['password'], # Lembre-se, isso não é seguro para produção!
                role=row['role']
            )
            # Adicionar ao banco (lógica a ser implementada)

        # --- Processa o ficheiro de Pontos de Venda (PDV) ---
        pos_contents = pos_file.file.read()
        pos_df = pd.read_excel(io.BytesIO(pos_contents))

        required_pos_cols = {'name', 'latitude', 'longitude'}
        if not required_pos_cols.issubset(pos_df.columns):
            raise HTTPException(status_code=400, detail="Ficheiro de PDVs com colunas em falta.")

        for index, row in pos_df.iterrows():
            print(f"A criar PDV: {row['name']}")
            pos_data = schemas.PointOfSaleCreate(
                name=row['name'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                # Trata o caso da coluna opcional não existir no Excel
                required_visits_per_week=row.get('required_visits_per_week', 1)
            )
            # Adicionar ao banco (lógica a ser implementada)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar os ficheiros: {e}")


    return {"message": f"Ficheiros processados com sucesso pelo admin: {current_admin.username}"}
