from app.db.database import SessionLocal 
from app.services.optimization_service import OptimizationService
from app.crud import crud_results 
from app.db import models
from app.db.models import OptimizationStatus
import sys

def run_optimization_background(run_id: int):

    #  Cria uma sessão de DB nova e independente para esta tarefa
    db = SessionLocal()
    run = None
    
    try:
        #  Obtem a 'Run' e marcá-la como 'RUNNING'
        run = db.query(models.OptimizationRun).filter(models.OptimizationRun.id == run_id).first()
        if not run:
            print(f"ERRO DE TAREFA: Run ID {run_id} não encontrado.")
            return

        run.status = OptimizationStatus.RUNNING
        db.commit()
        
        print(f"Iniciando otimização para Run ID: {run_id}...")

        # Executa a lógica de otimização completa 
        optimizer = OptimizationService(db)
        plano_semanal, pdvs_nao_atribuidos = optimizer.run_optimization()
        
        print(f"Otimização concluída para Run ID: {run_id}. Salvando resultados...")

        # Salva os resultados 
        # Passamos a 'run' existente para que o crud_results possa vinculá-la
        crud_results.save_optimization_results(
            db, 
            run, 
            plano_semanal, 
            pdvs_nao_atribuidos
        )

        #  Marca a 'Run' como 'COMPLETED' 
        run.status = OptimizationStatus.COMPLETED
        run.total_pdvs_assigned = sum(len(dia) for user_dias in plano_semanal.values() for dia in user_dias.values())
        run.total_pdvs_unassigned = len(pdvs_nao_atribuidos)
        db.commit()
        
        print(f"Run ID: {run_id} concluído e salvo com sucesso.")

    except Exception as e:
        print(f"!!! ERRO FATAL na Otimização (Run ID: {run_id}): {e} !!!")
        # traceback.print_exc() # Descomente para debug detalhado
        if run:
            run.status = OptimizationStatus.FAILED
            db.commit()
    finally:
        #  Fecha a sessão do DB é obrigatório
        db.close()
        print(f"Sessão do DB para Run ID: {run_id} fechada.")