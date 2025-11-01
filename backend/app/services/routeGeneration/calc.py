from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import traceback

from app.db.models import (
    user,
    dailyVisit,
    weaklyPlan,
    pointOfStop,
    optimizationRun,
    optimizationStatus
)

from ..funnel.priority_filter import (
    get_data_pool,
    filter_pdvs_by_haversine,
    calculate_priority_scores,
    select_realistic_pdv_pool_for_worker
)

from .google_use import _build_cost_matrix, _solve_route_with_ortools

def generate_and_save_schedules(db: Session, run_id: int, num_days: int = 5):
    """
    Função principal de geração de rotas e agendamentos.
    Usa OptimizationRun para rastrear execuções.
    """
    run = db.query(optimizationRun).filter(optimizationRun.id == run_id).first()
    if not run:
        print(f"Erro Crítico: Run ID {run_id} não encontrado. Saindo da tarefa.")
        return
    run.status = optimizationStatus.RUNNING
    db.commit()

    total_pdvs_assigned_run = 0
    total_pdvs_unassigned_run = 0

    try:
        print("Limpando agendamentos antigos...")
        db.query(dailyVisit).filter(dailyVisit.optimization_run_id != run_id).delete()
        db.query(weaklyPlan).filter(weaklyPlan.optimization_run_id != run_id).delete()

        all_pdvs, all_workers = get_data_pool(db)
        today = datetime.now().date()

        for worker in all_workers:
            geo_candidates = filter_pdvs_by_haversine(worker, all_pdvs)
            if not geo_candidates:
                continue

            prioritized_candidates = calculate_priority_scores(geo_candidates)
            if not prioritized_candidates:
                continue

            pdv_list_para_otimizar = select_realistic_pdv_pool_for_worker(
                worker, prioritized_candidates
            )
            if not pdv_list_para_otimizar:
                print(f"Nenhum PDV realista encontrado para {worker.full_name}.")
                continue

            print(f"Trabalhador {worker.full_name}: {len(pdv_list_para_otimizar)} PDVs realistas (Enviando ao Google).")

            cost_matrix, mapped_pdv_list = _build_cost_matrix(worker, pdv_list_para_otimizar, db)
            route_indices = _solve_route_with_ortools(cost_matrix)
            if not route_indices:
                print(f"Não foi encontrada solução de rota para {worker.full_name}.")
                continue

            new_weekly_plan = weaklyPlan(
                user_id=worker.id,
                optimization_run_id=run_id
            )
            db.add(new_weekly_plan)

            max_daily_time = worker.daily_work_duration_seconds
            max_stops_per_day = worker.max_visits_per_day or 999
            matrix_indices_optimal_order = [idx + 1 for idx in route_indices]
            worker_pdvs_assigned_count = 0

            for day in range(num_days):
                if not matrix_indices_optimal_order:
                    break

                current_day_time = 0
                current_day_stops = 0
                last_location_index = 0
                pdvs_scheduled_this_day_indices = []

                visit_date = today + timedelta(days=day)

                for matrix_index in matrix_indices_optimal_order:
                    if current_day_stops >= max_stops_per_day:
                        break

                    pdv_list_index = matrix_index - 1
                    pdv = mapped_pdv_list[pdv_list_index]

                    travel_to_pdv = cost_matrix[last_location_index][matrix_index]
                    service_time = pdv.visit_duration_seconds
                    travel_back_to_depot = cost_matrix[matrix_index][0]

                    total_time_if_added = (
                        current_day_time + travel_to_pdv + service_time + travel_back_to_depot
                    )

                    if total_time_if_added <= max_daily_time:
                        current_day_time += travel_to_pdv + service_time
                        current_day_stops += 1
                        pdvs_scheduled_this_day_indices.append(matrix_index)
                        last_location_index = matrix_index

                        new_visit = dailyVisit(
                            visit_date=visit_date,
                            status='Pendente',
                            user_id=worker.id,
                            point_of_stop_id=pdv.id,
                            optimization_run_id=run_id,
                        )
                        db.add(new_visit)
                        worker_pdvs_assigned_count += 1

                matrix_indices_optimal_order = [
                    idx for idx in matrix_indices_optimal_order if idx not in pdvs_scheduled_this_day_indices
                ]

            new_weekly_plan.total_pdvs_assigned = worker_pdvs_assigned_count
            total_pdvs_assigned_run += worker_pdvs_assigned_count

            unassigned_count = len(matrix_indices_optimal_order)
            total_pdvs_unassigned_run += unassigned_count

            if unassigned_count:
                print(f"AVISO: {unassigned_count} PDVs não alocados para {worker.full_name}.")
        
        run.status = optimizationStatus.COMPLETED
        run.total_pdvs_assigned = total_pdvs_assigned_run
        run.total_pdvs_unassigned = total_pdvs_unassigned_run
        db.commit()
        print("Agendamento salvo com sucesso.")

    except Exception as e:
        db.rollback()
        run.status = optimizationStatus.FAILED
        db.commit()
        print(f"Erro ao salvar agendamento no BD: {e}")
        print("!!!!!!!!!!! ERRO NO CÁLCULO EM SEGUNDO PLANO !!!!!!!!!!!")
        print(traceback.format_exc())

    print("Processamento de agendamento concluído.")