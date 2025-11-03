from sqlalchemy.orm import Session
from app.crud import crud_cache
from app.core.config import settings 
import httpx
from typing import Optional

_local_cache = {}

class DistanceService:
    def __init__(self, db: Session):
        self.db = db

    def get_duration(self, origem, destino) -> int:
        """
        Função principal JIT para obter a duração da viagem em segundos.
        """
        global _local_cache 
        
        origem_tipo = "user" if hasattr(origem, 'username') else "pos"
        destino_tipo = "pos" if hasattr(destino, 'name') else "user"
        
        cache_key = (origem_tipo, origem.id, destino_tipo, destino.id)

        if cache_key in _local_cache:
            return _local_cache[cache_key]

        db_duration = crud_cache.get_from_db_cache(
            self.db, origem_tipo, origem.id, destino_tipo, destino.id
        )
        if db_duration is not None:

            print(f"  -> CACHE HIT (DB): {origem_tipo} {origem.id} -> {destino_tipo} {destino.id}")
            _local_cache[cache_key] = db_duration
            return db_duration 

        if origem_tipo == "user":
            orig_lat, orig_lon = origem.start_latitude, origem.start_longitude
        else: 
            orig_lat, orig_lon = origem.latitude, origem.longitude

        if destino_tipo == "user":
            dest_lat, dest_lon = destino.start_latitude, destino.start_longitude
        else: 
            dest_lat, dest_lon = destino.latitude, destino.longitude

        print(f"!!! CHAMADA DE API: {origem_tipo} {origem.id} -> {destino_tipo} {destino.id} !!!")
        
        duration = self._call_google_maps_api(
            orig_lat, orig_lon, dest_lat, dest_lon
        )

        if duration is None:
            print(f"  -> AVISO: API falhou para {origem_tipo} {origem.id} -> {destino_tipo} {destino.id}. Usando penalidade.")
            duration = 999999 

        _local_cache[cache_key] = duration
        crud_cache.save_to_db_cache(
            self.db, origem_tipo, origem.id, destino_tipo, destino.id,
            distance_meters=0, 
            duration_seconds=duration
        )
        
        return duration

    def _call_google_maps_api(self, orig_lat, orig_lon, dest_lat, dest_lon) -> Optional[int]:

        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": f"{orig_lat},{orig_lon}",
            "destinations": f"{dest_lat},{dest_lon}",
            "mode": "driving",
            "departure_time": "now",
            "key": settings.GOOGLE_MAPS_API_KEY,
        }
        try:
            with httpx.Client() as client:
                r = client.get(url, params=params)
                r.raise_for_status()
                data = r.json()
                if data["status"] == "OK" and data["rows"][0]["elements"][0]["status"] == "OK":
                    element = data["rows"][0]["elements"][0]
                    duration = element.get("duration_in_traffic", {}).get("value") or element.get("duration", {}).get("value")
                    return duration
                return None
        except Exception as e:
            print(f"ERRO DE API: {e}")
            return None