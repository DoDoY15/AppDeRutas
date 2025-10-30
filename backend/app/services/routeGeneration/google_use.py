import googlemaps # type: ignore
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.db.models import DistanceCache 

from app.db.models import User, PointOfStop
from app.core.config import settings # Supondo que sua API key esteja aqui

GMAPS_CLIENT = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
TRAVEL_MODE = "driving" 

def calculate_weekly_schedule_for_worker(
    worker: User, 
    pdv_list: List[PointOfStop],
    num_days: int = 5
) -> Tuple[Dict[int, List[PointOfStop]], List[PointOfStop]]:

    if not pdv_list:
        return {}, []
    # Limites do trabalhador
    max_daily_time = worker.daily_work_duration_seconds
    # (Adicione este campo ao seu modelo User e rode a migração)
    max_stops_per_day = worker.max_visits_per_day or 999 
    
    # 1. Construir Matriz e 2. Resolver Rota Ótima
    cost_matrix, mapped_pdv_list = _build_cost_matrix(worker, pdv_list)
    route_indices = _solve_route_with_ortools(cost_matrix)
    
    if not route_indices:
         return {}, pdv_list 
    
    # Retorna todos como não alocados

    # 3. Empacotamento da Rota em Dias
    weekly_schedule = {}
    matrix_indices_optimal_order = [idx + 1 for idx in route_indices]

    for day in range(1, num_days + 1):
        if not matrix_indices_optimal_order: break 

        current_day_route_pdvs = []
        current_day_time = 0
        current_day_stops = 0
        last_location_index = 0
        pdvs_scheduled_this_day_indices = []

        for matrix_index in matrix_indices_optimal_order:
            
            if current_day_stops >= max_stops_per_day:
                break # Limite de visitas do dia

            pdv_list_index = matrix_index - 1
            pdv = mapped_pdv_list[pdv_list_index]

            travel_to_pdv = cost_matrix[last_location_index][matrix_index]
            service_time = pdv.average_service_time_seconds
            travel_back_to_depot = cost_matrix[matrix_index][0]

            total_time_if_added = current_day_time + travel_to_pdv + service_time + travel_back_to_depot

            if total_time_if_added <= max_daily_time:
                current_day_time += travel_to_pdv + service_time
                current_day_route_pdvs.append(pdv)
                current_day_stops += 1
                pdvs_scheduled_this_day_indices.append(matrix_index)
                last_location_index = matrix_index
            else:
                continue

        if current_day_route_pdvs:
            weekly_schedule[day] = current_day_route_pdvs

        matrix_indices_optimal_order = [
            idx for idx in matrix_indices_optimal_order if idx not in pdvs_scheduled_this_day_indices
        ]

    # 4. Aviso de PDVs não alocados
    unassigned_pdvs = [
        mapped_pdv_list[i-1] for i in matrix_indices_optimal_order
    ]
    
    return weekly_schedule, unassigned_pdvs

def _get_distance_google_maps(
    lat1: float, lon1: float, 
    lat2: float, lon2: float, 
    db: Session  # <--- PASSAR A SESSÃO DO BD
) -> int:
    """
    Busca a distância (em segundos) da API do Google Maps,
    usando sua tabela 'DistanceCache'.
    """
    origin = (lat1, lon1)
    dest = (lat2, lon2)
    
    # 1. Tenta buscar do cache do BD
    cached_result = db.query(DistanceCache).filter(
        DistanceCache.origin_lat == lat1,
        DistanceCache.origin_lng == lon1,
        DistanceCache.dest_lat == lat2,
        DistanceCache.dest_lng == lon2
    ).first()
    
    if cached_result:
        return cached_result.duration_seconds

    # 2. Se não achou, busca na API
    try:
        result = GMAPS_CLIENT.distance_matrix(
            origins=[origin],
            destinations=[dest],
            mode=TRAVEL_MODE
        )
        
        duration_seconds = result['rows'][0]['elements'][0]['duration']['value']
        distance_meters = result['rows'][0]['elements'][0]['distance']['value']
        
        # 3. Salva o novo resultado no cache do BD
        new_cache_entry = DistanceCache(
            origin_lat=lat1,
            origin_lng=lon1,
            dest_lat=lat2,
            dest_lng=lon2,
            duration_seconds=duration_seconds,
            distance_meters=distance_meters
        )
        db.add(new_cache_entry)
        # (O commit será feito pelo 'calc.py' no final)
        
        return duration_seconds

    except Exception as e:
        print(f"Erro ao chamar Google Maps API: {e}")
        return 999999 

def _build_cost_matrix(
    worker: User, 
    pdv_list: List[PointOfStop],
    db: Session  # <--- PASSAR A SESSÃO DO BD
) -> Tuple[List[List[int]], List[PointOfStop]]:
    """
    Monta a matriz de custo (tempo de viagem) para o OR-Tools.
    O ponto 0 é sempre o depósito (início/fim do trabalhador).
    """
    
    points = [
        {"id": "worker_start", "lat": worker.start_latitude, "lon": worker.start_longitude}
    ]
    for pdv in pdv_list:
        points.append({"id": pdv.id, "lat": pdv.latitude, "lon": pdv.longitude})

    num_points = len(points)
    matrix = [[0] * num_points for _ in range(num_points)]

    for i in range(num_points):
        for j in range(num_points):
            if i == j:
                continue
            
            p1 = points[i]
            p2 = points[j]
            
            # --- MODIFICAÇÃO AQUI ---
            # Passa o 'db' para a função de cache
            matrix[i][j] = _get_distance_google_maps(
                p1["lat"], p1["lon"], p2["lat"], p2["lon"], db
            )
            
    return matrix, pdv_list

def _solve_route_with_ortools(cost_matrix: List[List[int]]) -> List[int]:
    # ... (Seu código atual está perfeito)
    pass