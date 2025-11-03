from sqlalchemy.orm import Session
from typing import List, Dict, Any, Tuple
from app.db.models import User, PointOfStop
import sys

from app.services.distance_service import DistanceService
from app.services.priority_service import PriorityService
from app.services.haversine_service import HaversineService
from app.crud import crud_data_pool, crud_results
from app.services.optimization_logic.cost_calculator import CostCalculator
from app.services.optimization_logic.slot_finder import SlotFinder, OptimizationState


class OptimizationService:
    
    def __init__(self, db: Session):
        self.db = db
        
        # Serviços Auxiliares stateless

        self.distance_service = DistanceService(db)
        self.priority_service = PriorityService()
        self.haversine_service = HaversineService()

        # especialistas
        self.cost_calculator = CostCalculator(self.distance_service)
        self.slot_finder = SlotFinder(self.haversine_service, self.cost_calculator)
        
        # Dados de Entrada 
        self.workers: List[User] = []
        self.pdvs_priorizados: List[Tuple[PointOfStop, float]] = []
        
        # State
        self.plano_semanal: Dict[int, Dict[int, List[PointOfStop]]] = {}
        self.tempo_usado: Dict[int, Dict[int, float]] = {}
        self.optimization_state = OptimizationState(self.plano_semanal, self.tempo_usado)
        
        # Resultado 
        self.pdvs_nao_atribuidos: List[PointOfStop] = []

    # ======================================================================
    #  Optimization
    # ======================================================================

    def run_optimization(self) -> Tuple[Dict, List]:
        
        print("Iniciando otimização...")
        
        # --- ETAPA 1: Preparação ---
        success = self._setup_optimization()
        if not success:
            return {}, []

        # --- ETAPA 2: Lógica Principal (Delegação) ---
        print("4. Iniciando loop de inserção Híbrida JIT...")
        
        max_frequency = max(
            (pdv.visits_per_week for pdv, score in self.pdvs_priorizados if pdv.visits_per_week),
            default=1
        ) or 1

        for visit_number in range(1, max_frequency + 1):
            print(f"  -> Iniciando Passagem {visit_number}/{max_frequency}...")
            
            for pdv, score in self.pdvs_priorizados:
                
                if pdv.visits_per_week < visit_number:
                    continue

                melhor_lugar_encontrado = self.slot_finder.find_best_slot_for_pdv(
                    pdv, 
                    self.workers, 
                    self.optimization_state 
                )
                if melhor_lugar_encontrado:
                    (worker, dia, pos, novo_tempo) = melhor_lugar_encontrado
                    #  atualiza o estado
                    self.plano_semanal[worker.id][dia].insert(pos, pdv)
                    self.tempo_usado[worker.id][dia] = novo_tempo
                
                elif visit_number == 1 and pdv not in self.pdvs_nao_atribuidos:
                     self.pdvs_nao_atribuidos.append(pdv)

        # --- ETAPA 3: Limpeza Final ---
        print("5. Otimização concluída.")
        self._cleanup_unassigned_list()
        
        return self.plano_semanal, self.pdvs_nao_atribuidos

    # ======================================================================
    # === 2. MÉTODOS DE SETUP (Pequenos e limpos) ===
    # ======================================================================

    def _setup_optimization(self) -> bool:
        """(Auxiliar) Busca dados e inicializa as estruturas do plano."""
        print("1. Buscando dados (Workers e PDVs)...")
        self.workers, pdv_pool = crud_data_pool.get_data_pool(self.db)
        
        if not self.workers or not pdv_pool:
            print("Erro: Não há trabalhadores ou PDVs ativos.")
            return False
        
        print(f"Encontrados {len(self.workers)} trabalhadores e {len(pdv_pool)} PDVs.")

        print("2. Calculando prioridades globais...")
        self.pdvs_priorizados = self.priority_service.calculate_global_priority_scores(pdv_pool)

        print("3. Inicializando estruturas de plano...")
        self.plano_semanal.clear()
        self.tempo_usado.clear()
        self.plano_semanal.update({w.id: {1: [], 2: [], 3: [], 4: [], 5: []} for w in self.workers})
        self.tempo_usado.update({w.id: {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0} for w in self.workers})
        self.pdvs_nao_atribuidos = []
        return True

    def _cleanup_unassigned_list(self):
        """(Auxiliar) Limpa a lista de não atribuídos."""
        pdvs_atribuidos_ids = set()
        for plano_dia in self.plano_semanal.values():
            for lista_pdvs in plano_dia.values():
                for pdv in lista_pdvs:
                    pdvs_atribuidos_ids.add(pdv.id)
        
        self.pdvs_nao_atribuidos = [pdv for pdv in self.pdvs_nao_atribuidos if pdv.id not in pdvs_atribuidos_ids]