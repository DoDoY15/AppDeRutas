# app/crud/crud_pos.py

import io
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.db import models
from app.schemas.point_of_stop import PointOfStopCreate 
from typing import Tuple # Importe o 'Tuple'

# Retorna uma tupla: (criados, atualizados)
def process_and_load_pos(db: Session, pos_file: UploadFile) -> Tuple[int, int]:

    pos_file.file.seek(0)
    contents = pos_file.file.read()
    df = pd.read_excel(io.BytesIO(contents))
    
    # --- Sua Lógica de Limpeza (Perfeita) ---
    if 'ID' in df.columns:
        # CORREÇÃO PARA O ERRO 2: Força o ID a ser string
        df['ID'] = df['ID'].astype(str) 

    df = df.astype(object).where(pd.notnull(df), None)
    
    column_mapping = {
        'ID': 'external_id',
        'Nombre del PDV': 'name',
        'Cadena': 'chain',
        'Segmentación': 'segment', # Corrigi um typo seu: 'Segment' -> 'segment'
        'Canal del PDV': 'channel',
        'Regional': 'region', # Corrigi um typo seu: 'Region' -> 'region'
        'País': 'country', # Corrigi um typo seu: 'Country' -> 'country'
        'Ciudad': 'city', # Corrigi um typo seu: 'City' -> 'city'
        'Dirección': 'address', # Corrigi um typo seu: 'Address' -> 'address'
        'Latitud': 'latitude',
        'Longitud': 'longitude',
        'Activo': 'working_status', # Corrigi um typo seu: 'WorkingStatus' -> 'working_status'
        'Visitas semanales': 'visits_per_week',
        'Duración visita(horas)': 'visit_duration_hours',
        'Prioridad': 'priority'
    }
    df.rename(columns=column_mapping, inplace=True)

    if 'working_status' in df.columns:
        df['working_status'] = df['working_status'].apply(
            lambda x: True if str(x).lower() in ['yes', 'true', '1', 'sim', 'si', 'sí', 'activo'] else False
        )
    else:
        df['working_status'] = True 

    if 'visit_duration_hours' in df.columns:
        df['visit_duration_seconds'] = df['visit_duration_hours'].apply(
            lambda x: int(float(x) * 3600) if pd.notna(x) else 1800 
        )
    else:
        df['visit_duration_seconds'] = 1800
    # --- Fim da Sua Lógica de Limpeza ---
    
    pos_data_list = df.to_dict('records')
    schema_keys = set(PointOfStopCreate.model_fields.keys())

    # --- INÍCIO DA LÓGICA DE UPSERT ---
    
    # 1. Busca todos os PDVs existentes no DB DE UMA VEZ
    existing_pdvs_query = db.query(models.PointOfStop).all()
    existing_pdvs_map = {str(pdv.external_id): pdv for pdv in existing_pdvs_query}
    
    criados_count = 0
    atualizados_count = 0
    
    for pos_data in pos_data_list:
        
        external_id = pos_data.get('external_id')
        if not external_id or external_id == 'None':
            continue # Pula linha sem ID

        # 2. Verifica se o PDV já existe
        if external_id in existing_pdvs_map:
            # --- SE EXISTIR: ATUALIZE ---
            pdv_existente = existing_pdvs_map[external_id]
            
            # Atualiza todos os campos (exceto ID)
            for key, value in pos_data.items():
                if key != 'external_id' and hasattr(pdv_existente, key) and value is not None:
                    setattr(pdv_existente, key, value)
            
            atualizados_count += 1
            
        else:
            # --- SE NÃO EXISTIR: CRIE ---
            schema_data = {
                key: pos_data[key] for key in pos_data 
                if key in schema_keys and pos_data[key] is not None
            }
            
            try:
                # Valida com o Schema (Pydantic V2)
                pos_schema = PointOfStopCreate(**schema_data)
                # Converte o schema para dados do modelo
                db_pos = models.PointOfStop(**pos_schema.model_dump()) 
                db.add(db_pos)
                criados_count += 1
            except Exception as e:

                print(f"Erro ao validar/criar PDV {external_id}: {e} - Dados: {schema_data}")
                continue 

    return (criados_count, atualizados_count) 