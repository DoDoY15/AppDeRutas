from app.db.database import SessionLocal
from app.services.optimization_service import OptimizationService
from app.crud import crud_results, crud_data_pool
from app.db import models
from app.db.models import OptimizationStatus, PointOfStop 

def run_optimization_background(run_id: int):
    """
    Background Task
    """
    
    db = SessionLocal()
    run = None
    
    try:

        run = db.query(models.OptimizationRun).filter(models.OptimizationRun.id == run_id).first()
        run.status = OptimizationStatus.RUNNING
        db.commit()
        
        # ... (Executa a otimização) ...
        optimizer = OptimizationService(db)
        plano_semanal, pdvs_nao_atribuidos_lista = optimizer.run_optimization()
        
        # ... (Salva os resultados) ...
        crud_results.save_optimization_results(
            db, run, plano_semanal, pdvs_nao_atribuidos_lista
        )
        
        print("Calculando métricas finais...")
        
        run.status = OptimizationStatus.COMPLETED

        _ , all_pdvs_in_pool = crud_data_pool.get_data_pool(db)
        total_pdvs_no_sistema = len(all_pdvs_in_pool)

        visit_count_map = {} 
        total_visitas_agendadas = 0
        for user_dias in plano_semanal.values():
            for dia_de_visitas in user_dias.values():
                for pdv in dia_de_visitas:
                    visit_count_map[pdv.id] = visit_count_map.get(pdv.id, 0) + 1
                    total_visitas_agendadas += 1

        pdvs_totalmente_atendidos = 0
        total_visitas_requeridas = 0
        
        for pdv in all_pdvs_in_pool:
            required_visits = pdv.visits_per_week
            actual_visits = visit_count_map.get(pdv.id, 0)
            
            total_visitas_requeridas += required_visits

            if actual_visits >= required_visits:
                pdvs_totalmente_atendidos += 1
        
        pdvs_nao_totalmente_atendidos = total_pdvs_no_sistema - pdvs_totalmente_atendidos
        visitas_faltantes = total_visitas_requeridas - total_visitas_agendadas

        run.total_pdvs_assigned = pdvs_totalmente_atendidos 
        run.total_pdvs_unassigned = pdvs_nao_totalmente_atendidos 
        run.total_visits_missed = visitas_faltantes 
        
        db.commit()
        
        print(f"Run ID: {run_id} concluído e salvo com sucesso.")

    except Exception as e:
        print(f"!!! ERRO FATAL na Otimização (Run ID: {run_id}): {e} !!!")
        if run:
            run.status = OptimizationStatus.FAILED
            db.commit()
        
    finally:
        db.close()