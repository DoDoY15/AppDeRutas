from sqlalchemy.orm import Session
from typing import List, Tuple
from app.db.models import PointOfStop, User, UserRole
from datetime import datetime, date
from math import radians, sin, cos, sqrt, atan2
import app.services.funnel.haversine as haversine

def get_data_pool(db: Session) -> Tuple[List[PointOfStop], List[User]]:

    # 1. Busca PDVs que precisam de visita
    pdv_pool = db.query(PointOfStop).filter(
        PointOfStop.visits_per_week > 0,
        PointOfStop.WorkingStatus == True 
    ).all()

    # 2. Busca trabalhadores
    workers = db.query(User).filter(
        User.role == UserRole.USER, 
        User.WorkingStatus == True
    ).all()

    return pdv_pool, workers

# ==============================================================
# =========== CONFIGURACION DE PESOS Y PRIORIDAD ===============
# ==============================================================
W_ATRASOS = 1.5           # Peso para cada dia desde a última visita
W_FREQUENCIA = 1.0        # Peso para a frequência semanal 
W_FLAG_PRIORIDAD = 1.0    # flag de prioridade manual
W_FLAG_DIST = 2.0         # Distancia entre worker e pdv 
# ==============================================================

R = 6371.0

HAVERSINE_THRESHOLD_KM = 75.0 

def filter_pdvs_by_haversine(
    worker: User, 
    pdv_pool: List[PointOfStop]
) -> List[Tuple[PointOfStop, float]]:
    """
    Filtro Rápido: Retorna (PDV, distancia) apenas para PDVs dentro do raio.
    """
    worker_lat, worker_lon = worker.start_latitude, worker.start_longitude
    candidates = []
    for pdv in pdv_pool:
        distance = haversine(worker_lat, worker_lon, pdv.latitude, pdv.longitude)
        if distance <= HAVERSINE_THRESHOLD_KM:
            candidates.append((pdv, distance))
    return candidates

# ==============================================================
# ============  LÓGICA DE PRIORIDADE ============
# ==============================================================
def calculate_priority_scores(
    candidates_with_distance: List[Tuple[PointOfStop, float]]
) -> List[Tuple[PointOfStop, float]]:

    weighted_list = []
    default_date = date(1970, 1, 1)
    today = datetime.now().date()

    for pdv, haversine_distance in candidates_with_distance:
        # --- 1. Fator Atraso (W_ATRASOS) ---
        last_visit = pdv.last_visited_at or default_date
        dias_desde_visita = (today - last_visit).days
        # --- 2. Fator Frequência (W_FREQUENCIA) ---
        frequencia = pdv.visits_per_week
        # --- 3. Fator Flag (W_FLAG_PRIORIDAD) ---
        flag_prioritaria = 1 if pdv.priority else 0
        # --- 4. Fator Distância (W_FLAG_DIST) ---
        fator_distancia = haversine_distance
        # --- CÁLCULO FINAL DO SCORE (Sua fórmula, agora em Python) ---
        priority_score = (dias_desde_visita * W_ATRASOS) + \
                         (frequencia * W_FREQUENCIA) + \
                         (flag_prioritaria * W_FLAG_PRIORIDAD) - \
                         (fator_distancia * W_FLAG_DIST)

        weighted_list.append((pdv, priority_score))

    weighted_list.sort(key=lambda item: item[1], reverse=True)
    
    return weighted_list


def select_realistic_pdv_pool_for_worker(
    worker: User, 
    prioritized_candidates: List[Tuple[PointOfStop, float]]) -> List[PointOfStop]:

    if not worker.daily_work_duration_seconds:
        return []
    
    MAX_TEMPO_SEMANAL = worker.daily_work_duration_seconds*5 
    tempo_estimado_total = 0
    pdvs_to_realy_optimize = []

    for pdv, score in prioritized_candidates:

        work_time = pdv.visit_duration_seconds
    
        dist_haversine_km = haversine(
                worker.start_latitude, worker.start_longitude,
                pdv.latitude, pdv.longitude)
        aprox_time_to_go = (dist_haversine_km * 1.4 / 40) * 3600
        spend_total_pdv = work_time + aprox_time_to_go

        if ( aprox_time_to_go + spend_total_pdv) <= MAX_TEMPO_SEMANAL:
                tempo_estimado_total += spend_total_pdv
                pdvs_to_realy_optimize.append(pdv)
        else: 
            break

    return pdvs_to_realy_optimize
    