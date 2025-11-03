# app/services/optimization_logic/cost_calculator.py

from app.db.models import User, PointOfStop
from app.services.distance_service import DistanceService
from typing import List

class CostCalculator:

    """Calcula o custo JIT de inserir um PDV em uma rota."""

    def __init__(self, distance_service: DistanceService):
        self.get_duration = distance_service.get_duration

    def calculate_insertion_cost(
        self, 
        worker: User, 
        rota: List[PointOfStop], 
        pdv_para_inserir: PointOfStop, 
        i: int
    ) -> float:
        
        if not rota:
            custo_ida = self.get_duration(worker, pdv_para_inserir)
            custo_volta = self.get_duration(pdv_para_inserir, worker)
            return custo_ida + custo_volta
        if i == 0:
            pdv_A = rota[0]
            custo_antigo = self.get_duration(worker, pdv_A)
            custo_novo = self.get_duration(worker, pdv_para_inserir) + self.get_duration(pdv_para_inserir, pdv_A)
            return custo_novo - custo_antigo
        if i == len(rota):
            pdv_Z = rota[-1]
            custo_antigo = self.get_duration(pdv_Z, worker)
            custo_novo = self.get_duration(pdv_Z, pdv_para_inserir) + self.get_duration(pdv_para_inserir, worker)
            return custo_novo - custo_antigo
            
        pdv_B = rota[i-1]
        pdv_C = rota[i]
        custo_antigo = self.get_duration(pdv_B, pdv_C)
        custo_novo = self.get_duration(pdv_B, pdv_para_inserir) + self.get_duration(pdv_para_inserir, pdv_C)
        return custo_novo - custo_antigo