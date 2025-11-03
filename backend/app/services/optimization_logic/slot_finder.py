# app/services/optimization_logic/slot_finder.py

from app.db.models import User, PointOfStop
from app.services.haversine_service import HaversineService
from .cost_calculator import CostCalculator
from typing import List, Dict, Tuple, Optional
import sys

class OptimizationState:
    def __init__(self, plano_semanal: Dict, tempo_usado: Dict):
        self.plano_semanal = plano_semanal
        self.tempo_usado = tempo_usado

BestSlotType = Optional[Tuple[User, int, int, float]]

class SlotFinder:
    """Encontra o melhor slot (worker, dia, posição) para um PDV."""
    
    def __init__(self, haversine_service: HaversineService, cost_calculator: CostCalculator):
        self.haversine_service = haversine_service
        self.cost_calculator = cost_calculator

    def find_best_slot_for_pdv(
        self, 
        pdv: PointOfStop, 
        workers: List[User], 
        state: OptimizationState
    ) -> BestSlotType:
        
        candidate_workers = self.haversine_service.get_candidate_workers(pdv, workers)
        
        melhor_custo_adicional = sys.float_info.max
        melhor_lugar_encontrado = None 

        for worker in candidate_workers:
            for dia in range(1, 6):
                
                rota_atual = state.plano_semanal[worker.id][dia]
                
                if any(p.id == pdv.id for p in rota_atual): continue 
                if len(rota_atual) >= (worker.max_visits_per_day or 99): continue

                for posicao in range(len(rota_atual) + 1):
                    
                    #  Custo de Deslocamento 
                    custo_adicional_deslocamento = self.cost_calculator.calculate_insertion_cost(
                        worker, rota_atual, pdv, posicao
                    )

                    #  Custo da Visita 
                    tempo_visita_pdv = pdv.visit_duration_seconds or 1800

                    #  Tempo total de TRABALHO (Ignora deslocamento)
                    
                    novo_tempo_de_TRABALHO = state.tempo_usado[worker.id][dia] + tempo_visita_pdv
                    
                    worker_daily_duration = (worker.daily_work_duration_seconds or 28800)
                    
                    #  Checamos o limite do dia APENAS contra o tempo de TRABALHO
                    if novo_tempo_de_TRABALHO > worker_daily_duration:
                        continue # Estoura o tempo de trabalho do dia

                    #  Se "coube" no dia, vemos se é o "melhor" (menor deslocamento)
                    if custo_adicional_deslocamento < melhor_custo_adicional:
                        melhor_custo_adicional = custo_adicional_deslocamento

                        # Salvamos o tempo de TRABALHO para o próximo cálculo
                        melhor_lugar_encontrado = (worker, dia, posicao, novo_tempo_de_TRABALHO)
                        
        return melhor_lugar_encontrado