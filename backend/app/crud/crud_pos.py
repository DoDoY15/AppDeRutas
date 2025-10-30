import io
import pandas as pd
import numpy as np 
from sqlalchemy.orm import Session
from fastapi import UploadFile

from ..db import models
from ..schemas.point_of_stop import PointOfStopCreate 

def process_and_load_pos(db: Session, pos_file: UploadFile) -> int:

    pos_file.file.seek(0)
    contents = pos_file.file.read()
    df = pd.read_excel(io.BytesIO(contents))
    if 'ID' in df.columns:
        df['ID'] = df['ID'].astype(str)

    df = df.astype(object).where(pd.notnull(df), None)

    # 3. Mapeamento
    column_mapping = {
        'ID': 'external_id',
        'Nombre del PDV': 'name',
        'Cadena': 'chain',
        'Segmentación': 'Segment',
        'Canal del PDV': 'channel',
        'Regional': 'Region',
        'País': 'Country',
        'Ciudad': 'City',
        'Dirección': 'Address',
        'Latitud': 'latitude',
        'Longitud': 'longitude',
        'Activo': 'WorkingStatus',
        'Visitas semanales': 'visits_per_week',
        'Duración visita(horas)': 'visit_duration_hours',
        'Prioridad': 'priority'
    }

    df.rename(columns=column_mapping, inplace=True)

    if 'WorkingStatus' in df.columns:
        df['WorkingStatus'] = df['WorkingStatus'].apply(
            lambda x: True if str(x).lower() in ['yes', 'true', '1', 'sim', 'si', 'sí'] else False
        )
    else:
        df['WorkingStatus'] = True 

    if 'visit_duration_hours' in df.columns:
        df['visit_duration_seconds'] = df['visit_duration_hours'].apply(
            lambda x: int(x * 3600) if x is not None else 1800 
        )
    else:
        df['visit_duration_seconds'] = 1800

    pos_data_list = df.to_dict('records')
    schema_keys = set(PointOfStopCreate.model_fields.keys())
    objects_to_add = []
    
    for pos_data in pos_data_list:

        schema_data = {
            key: pos_data[key] for key in pos_data 
            if key in schema_keys and pos_data[key] is not None
        }
        
        try:
            pos_schema = PointOfStopCreate(**schema_data)
        except Exception as e:
            print(f"Erro ao validar PDV: {e} - Dados: {schema_data}")
            continue 

        db_pos = models.PointOfStop(**pos_schema.dict())
        objects_to_add.append(db_pos)
    db.add_all(objects_to_add)

    
    return len(objects_to_add)

