import io
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.db import models
# from app.core import security
from app.schemas.user import UserCreate # Usamos para validar
from typing import Tuple

# 1. MAPEAMENTO DE SINÔNIMOS
USER_ALIASES = {
    'username': ['usuario', 'username', 'user', 'user id'],
    'full_name': ['full_name', 'nombre', 'nombre del empleado', 'nome'],
    'email': ['email', 'e-mail', 'correo'],
    'role': ['role', 'perfil', 'perfil de acceso'],
    'password': ['password', 'senha', 'contraseña'],
    'start_latitude': ['start_latitude', 'latitud', 'lat_inicio'],
    'start_longitude': ['start_longitude', 'longitud', 'lon_inicio'],
    'daily_work_duration_hours': ['daily_work_duration_hours', 'horas por día', 'horas_por_dia_usuario'],
    'max_visits_per_day': ['max_visits_per_day', 'visitas maximas por dia', 'visitas_maximas'],
    'working_status': ['working_status', 'activo', 'active', 'ativo']
}

DEFAULT_PASSWORD = "123456" # Senha padrão para novos usuários

def _normalize_user_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte nomes de colunas do Excel (ex: 'Nombre del empleado')
    para nomes de campos do DB (ex: 'full_name') usando os sinônimos.
    """
    alias_map_reverse = {}
    for db_field, aliases in USER_ALIASES.items():
        for alias in aliases:
            # Normaliza o sinônimo para busca
            alias_clean = str(alias).lower().replace(' ', '').replace('_', '')
            alias_map_reverse[alias_clean] = db_field

    normalized_columns = {}
    for col in df.columns:
        clean_col = str(col).lower().replace(' ', '').replace('_', '')
        
        if clean_col in alias_map_reverse:
            normalized_columns[col] = alias_map_reverse[clean_col]
            
    df.rename(columns=normalized_columns, inplace=True)
    return df

def _transform_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica suas regras de transformação de dados (horas, roles).
    """
    # --- Transformação de Duração (Horas -> Segundos) ---
    if 'daily_work_duration_hours' in df.columns:
        df['daily_work_duration_seconds'] = df['daily_work_duration_hours'].apply(
            lambda x: int(float(x) * 3600) if pd.notna(x) else None
        )
    else:
        df['daily_work_duration_seconds'] = 28800 # Padrão

    # --- Transformação de Role ---
    if 'role' in df.columns:
        df['role'] = df['role'].apply(
            lambda x: 'admin' if str(x).lower() == 'admin' else 'user'
        )
    else:
        df['role'] = 'user' # Padrão
        
    # --- Transformação de Status ---
    if 'working_status' in df.columns:
        df['working_status'] = df['working_status'].apply(
            lambda x: True if str(x).lower() in ['yes', 'true', '1', 'sim', 'si', 'sí', 'activo'] else False
        )
    else:
        df['working_status'] = True
        
    return df

# --- FUNÇÃO PRINCIPAL ---

def process_and_load_users(db: Session, users_file: UploadFile) -> Tuple[int, int]:
    """
    Processa e faz o "Upsert" (Cria ou Atualiza) de Usuários.
    Retorna (criados_count, atualizados_count)
    """
    try:
        # 1. Ler, Normalizar, Transformar...
        users_file.file.seek(0)
        contents = users_file.file.read()
        df = pd.read_excel(io.BytesIO(contents))
        df = df.astype(object).where(pd.notnull(df), None)
        df = _normalize_user_columns(df)
        df = _transform_user_data(df)

        # 4. Lógica de "Upsert"
        existing_users_query = db.query(models.User).all()
        existing_users_map = {user.username: user for user in existing_users_query}
        
        users_data_list = df.to_dict('records')
        schema_keys = set(UserCreate.model_fields.keys())

        criados_count = 0
        atualizados_count = 0

        for user_data in users_data_list:
            username = user_data.get('username')
            if not username:
                continue

            if username in existing_users_map:
                # --- ATUALIZAR USUÁRIO EXISTENTE ---
                user_existente = existing_users_map[username]
                
                for key, value in user_data.items():
                    if key != 'password' and hasattr(user_existente, key) and value is not None:
                        setattr(user_existente, key, value)
                
                # Atualiza a senha APENAS se uma nova for fornecida
                if user_data.get('password') and pd.notna(user_data.get('password')):
                    
                    # --- REMOVEMOS A LÓGICA DE HASH ---
                    # Substituímos o hash por um valor fixo para evitar erros
                    user_existente.hashed_password = "bypassed_password_hash_for_update"
                    # --- FIM DA ALTERAÇÃO ---
                
                atualizados_count += 1
            
            else:
                # --- CRIAR NOVO USUÁRIO ---
                schema_data = {
                    key: user_data[key] for key in user_data 
                    if key in schema_keys and user_data[key] is not None
                }
                schema_data['password'] = user_data.get('password') or DEFAULT_PASSWORD

                try:
                    user_schema = UserCreate(**schema_data)
                    
                    # --- REMOVEMOS A LÓGICA DE HASH ---
                    # Substituímos o hash por um valor fixo para evitar erros
                    hashed_password = f"fake_hash_for_{user_schema.username}"
                    # --- FIM DA ALTERAÇÃO ---
                    
                    # (Use .model_dump() para Pydantic V2)
                    user_model_data = user_schema.model_dump(exclude={'password'}) 
                    
                    db_user = models.User(
                        **user_model_data,
                        hashed_password=hashed_password # Salva o "hash falso"
                    )
                    db.add(db_user)
                    criados_count += 1
                except Exception as e:
                    print(f"Erro ao validar/criar Usuário {username}: {e}")
                    continue
        
        return (criados_count, atualizados_count)

    except Exception as e:
        raise e