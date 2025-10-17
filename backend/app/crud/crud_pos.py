import io
import pandas as pd

from sqlalchemy.orm import Session
from fastapi import UploadFile

from ..db import models
from ..schemas import PointOfStopBase as schemas


def process_and_load_pos(db : Session , file: UploadFile) -> int:

    contents = file.file.read()
    df = pd.read_excel(io.BytesIO(contents))

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
    df = df.rename(columns=column_mapping, inplace=True)

    df['WorkingStatus'] = df['WorkingStatus'].apply(lambda x: True if str(x).lower() in ['yes', 'true', '1', 'sim' , 'si', 'Sí'] else False)

    for _, row in df.iterrows():
        pos_data_dict = row.to_dict()
        pos_schema = schemas.PointOfStopCreate(**pos_data_dict)
        db_pos = models.PointOfStop(**pos_schema.dict())
        db.add(db_pos)

    return len(df)