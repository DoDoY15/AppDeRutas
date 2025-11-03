# app/services/haversine_service.py

from typing import List
from app.db.models import PointOfStop, User
from math import radians, sin, cos, sqrt, atan2

# ==============================================================
# ================== CONFIGURAÇÕES HAVERSINE ===================
# ==============================================================
R = 6371.0  # Raio da Terra em quilômetros
HAVERSINE_THRESHOLD_KM = 75.0  # O raio máximo para um worker ser "candidato"
# ==============================================================

class HaversineService:
    """
    Responsável por filtrar geograficamente usando a fórmula Haversine 
    """
    def _haversine_formula(self, lat1, lon1, lat2, lon2) -> float:

        dLat = radians(lat2 - lat1)
        dLon = radians(lon2 - lon1)
        lat1 = radians(lat1)
        lat2 = radians(lat2)

        a = sin(dLat/2)**2 + cos(lat1) * cos(lat2) * sin(dLon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        return distance
    
    def get_candidate_workers(
        self, 
        pdv: PointOfStop, 
        all_workers: List[User]
    ) -> List[User]:
        
        if not pdv.latitude or not pdv.longitude:
            return []

        candidate_workers = []
        
        for worker in all_workers:
            if not worker.start_latitude or not worker.start_longitude:
                continue
            distance = self._haversine_formula(
                worker.start_latitude, worker.start_longitude,
                pdv.latitude, pdv.longitude
            )
            
            if distance <= HAVERSINE_THRESHOLD_KM:
                candidate_workers.append(worker)
                
        return candidate_workers