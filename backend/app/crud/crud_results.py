from sqlalchemy.orm import Session
from typing import List, Dict
from app.db.models import PointOfStop, OptimizationRun, DailyVisit, WeeklyPlan, VisitStatus
from datetime import date, timedelta

def _get_next_monday() -> date:
    today = date.today()
    days_ahead = (0 - today.weekday() + 7) % 7
    if days_ahead == 0: days_ahead = 7
    return today + timedelta(days=days_ahead)

def save_optimization_results(
    db: Session,
    optimization_run: OptimizationRun, # <-- MUDANÇA: Recebe a Run
    plano_semanal: Dict[int, Dict[int, List[PointOfStop]]],
    pdvs_nao_atribuidos_global: List[PointOfStop] # (Este não estamos usando, mas pode ser útil)
):
    """
    Salva os resultados da otimização vinculados a uma OptimizationRun existente.
    """
    
    start_of_week = _get_next_monday()
    print(f"Salvando resultados para o Run ID: {optimization_run.id}...")
    
    all_new_objects = []

    try:
        for user_id, dias_plan in plano_semanal.items():
            user_assigned_count = sum(len(pdvs) for pdvs in dias_plan.values())
            if user_assigned_count == 0:
                continue

            # 1. Cria o WeeklyPlan
            weekly_plan = WeeklyPlan(
                user_id=user_id,
                total_pos_assigned=user_assigned_count,
                # 2. VINCULA o WeeklyPlan à OptimizationRun existente
                optimization_run_id=optimization_run.id 
            )
            all_new_objects.append(weekly_plan)

            # 3. Itera e cria as DailyVisits
            for dia_num, pdvs_in_dia in dias_plan.items():
                current_visit_date = start_of_week + timedelta(days=dia_num - 1)
                
                for order_index, pdv in enumerate(pdvs_in_dia):
                    daily_visit = DailyVisit(
                        visit_date=current_visit_date,
                        status=VisitStatus.PENDING,
                        user_id=user_id,
                        point_of_stop_id=pdv.id,
                        visit_order=order_index + 1,
                        # 4. VINCULA a DailyVisit à OptimizationRun existente
                        optimization_run_id=optimization_run.id
                    )
                    all_new_objects.append(daily_visit)

        db.add_all(all_new_objects)
        db.commit()
        
        print(f"Sucesso: {len(all_new_objects)} objetos salvos no DB.")
        
    except Exception as e:
        db.rollback()
        print(f"ERRO AO SALVAR RESULTADOS: {e}")
        raise e