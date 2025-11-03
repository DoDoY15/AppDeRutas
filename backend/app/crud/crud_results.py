from sqlalchemy.orm import Session
from typing import List, Dict
from app.db.models import PointOfStop, OptimizationRun, DailyVisit, WeeklyPlan, VisitStatus , User
from datetime import date, timedelta
from app.services.distance_service import DistanceService



def _get_next_monday() -> date:
    today = date.today()
    days_ahead = (0 - today.weekday() + 7) % 7
    if days_ahead == 0: days_ahead = 7
    return today + timedelta(days=days_ahead)

def _seconds_to_time_str(seconds: float) -> str:
    """Converte segundos (float) para uma string de tempo "HH:MM"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours:02}:{minutes:02}"

def _time_str_to_seconds(time_str: str) -> float:
    """Converte uma string "HH:MM" de volta para segundos"""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return (hours * 3600) + (minutes * 60)
    except:
        return 0

def save_optimization_results(
    db: Session,
    optimization_run: OptimizationRun, 
    plano_semanal: Dict[int, Dict[int, List[PointOfStop]]],
    pdvs_nao_atribuidos_global: List[PointOfStop] 
):
    
    distance_service = DistanceService(db)  
    start_of_week = _get_next_monday()
    print(f"Salvando resultados para o Run ID: {optimization_run.id}...")
    
    all_new_objects = []

    user_ids = list(plano_semanal.keys())
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {user.id: user for user in users}

    try:
        for user_id, dias_plan in plano_semanal.items():
            user = user_map.get(user_id)
            if not user:
                continue

            user_assigned_count = sum(len(pdvs) for pdvs in dias_plan.values())
            if user_assigned_count == 0:
                continue

            #  Cria o WeeklyPlan
            weekly_plan = WeeklyPlan(
                user_id=user_id,
                total_pos_assigned=user_assigned_count,
                # VINCULA o WeeklyPlan à OptimizationRun existente
                optimization_run_id=optimization_run.id 
            )
            all_new_objects.append(weekly_plan)

            # Itera e cria as DailyVisits
            for dia_num, pdvs_in_dia in dias_plan.items():
                if not pdvs_in_dia:
                    continue

                current_visit_date = start_of_week + timedelta(days=dia_num - 1)

                # --- LÓGICA DE CÁLCULO DE TEMPO ---
                # Assume que o dia de trabalho começa às 09:00
                current_time_seconds = _time_str_to_seconds("09:00") 
                previous_stop = user # O dia começa na "casa" do trabalhado

                #  Itera sobre os PDVs na ordem correta
                for order_index, pdv in enumerate(pdvs_in_dia):
                    
                    # --- CÁLCULO DE DESLOCAMENTO (CACHE HIT!) ---
                    travel_duration_seconds = distance_service.get_duration(previous_stop, pdv)
                    
                    # --- CÁLCULO DE HORÁRIOS ---
                    current_time_seconds += travel_duration_seconds
                    arrival_time_str = _seconds_to_time_str(current_time_seconds)
                    
                    visit_duration_seconds = pdv.visit_duration_seconds or 1800
                    current_time_seconds += visit_duration_seconds
                    departure_time_str = _seconds_to_time_str(current_time_seconds)
                    
                    # --- FIM DO CÁLCULO ---
                    
                    daily_visit = DailyVisit(
                        visit_date=current_visit_date,
                        status=VisitStatus.PENDING,
                        user_id=user_id,
                        point_of_stop_id=pdv.id,
                        visit_order=order_index + 1,
                        optimization_run_id=optimization_run.id,
                        
                        # --- SALVA OS NOVOS DADOS ---
                        duration_from_previous_seconds=travel_duration_seconds,
                        estimated_arrival_time=arrival_time_str,
                        estimated_departure_time=departure_time_str
                    )
                    all_new_objects.append(daily_visit)
                    
                    # O "ponto anterior" para o próximo loop é o PDV atual
                    previous_stop = pdv 

        db.add_all(all_new_objects)
        db.commit()
        
        print(f"Sucesso: {len(all_new_objects)} objetos salvos no DB.")
        
    except Exception as e:
        db.rollback()
        print(f"ERRO AO SALVAR RESULTADOS: {e}")
        raise e