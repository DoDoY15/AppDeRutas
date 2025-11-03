# app/crud/crud_cache.py

from sqlalchemy.orm import Session
from app.db import models
from typing import Optional

def get_from_db_cache(
    db: Session,
    origem_tipo: str,
    origem_id: int,
    destino_tipo: str,
    destino_id: int
) -> Optional[int]:
    """
    Busca no banco de dados (UserDistanceCache ou POSDistanceCache)
    pela duração de uma viagem já calculada.
    """
    duration = None
    
    if origem_tipo == "user" and destino_tipo == "pos":
        cache_entry = db.query(models.UserDistanceCache).filter(
            models.UserDistanceCache.origin_id == origem_id,
            models.UserDistanceCache.dest_id == destino_id
        ).first()
        if cache_entry:
            duration = cache_entry.duration_seconds
            
    elif origem_tipo == "pos" and destino_tipo == "pos":
        cache_entry = db.query(models.POSDistanceCache).filter(
            models.POSDistanceCache.origin_pos_id == origem_id,
            models.POSDistanceCache.dest_pos_id == destino_id
        ).first()
        if cache_entry:
            duration = cache_entry.duration_seconds
            
    # Adicione a lógica para "pos" -> "user" se precisar cachear a volta pra casa
    return duration


def save_to_db_cache(
    db: Session,
    origem_tipo: str,
    origem_id: int,
    destino_tipo: str,
    destino_id: int,
    distance_meters: int,
    duration_seconds: int
):
    """
    Salva um novo resultado de distância/duração no banco de dados.
    """
    try:
        if origem_tipo == "user" and destino_tipo == "pos":
            db_cache = models.UserDistanceCache(
                origin_id=origem_id, dest_id=destino_id,
                distance_meters=distance_meters, duration_seconds=duration_seconds
            )
        elif origem_tipo == "pos" and destino_tipo == "pos":
            db_cache = models.POSDistanceCache(
                origin_pos_id=origem_id, dest_pos_id=destino_id,
                distance_meters=distance_meters, duration_seconds=duration_seconds
            )
        else:
            return

        db.add(db_cache)
        db.commit()
    except Exception:
        # Ignora falhas (ex: UniqueConstraint) se outra execução salvou o dado
        db.rollback()