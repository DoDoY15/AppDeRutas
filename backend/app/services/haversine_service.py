from typing import List
from app.db.models import PointOfStop, User
from math import radians, sin, cos, sqrt, atan2
from app.services import haversine

# ==============================================================
# ================== CONFIGURAÇÕES HAVERSINE ===================
# ==============================================================

HAVERSINE_THRESHOLD_KM = 75.0  # O raio máximo para um worker ser "candidato"

# ==============================================================

class HaversineService:
    """
    Responsável por filtrar geograficamente usando a fórmula Haversine
    """
    
    def get_candidate_workers(
        self, 
        pdv: PointOfStop, 
        all_workers: List[User]
    ) -> List[User]:
        
        """
        Recebe UM PDV e a lista COMPLETA de trabalhadores.
        Retorna uma lista de trabalhadores "candidatos" que estão
        dentro do raio de `HAVERSINE_THRESHOLD_KM`.
        """
        
        # Garante que o PDV tem coordenadas
        if not pdv.latitude or not pdv.longitude:
            return []

        candidate_workers = []
        
        for worker in all_workers:
            # Garante que o trabalhador tem coordenadas
            if not worker.start_latitude or not worker.start_longitude:
                continue

            # Calcula a distância em linha reta (gratuita)
            distance = haversine(
                worker.start_latitude, worker.start_longitude,
                pdv.latitude, pdv.longitude
            )
            
            # Se estiver dentro do raio, ele é um candidato
            if distance <= HAVERSINE_THRESHOLD_KM:
                candidate_workers.append(worker)
                
        return candidate_workers