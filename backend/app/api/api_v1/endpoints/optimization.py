from fastapi import ( APIRouter, Depends, HTTPException, BackgroundTasks)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Any

from app.dependencies import get_db 
from app.services.optimization_task import run_optimization_background 

from app.db.models import OptimizationRun, OptimizationStatus, WeeklyPlan, User, DailyVisit

from app.services import optimization_PG as optimization_logic

router = APIRouter()

@router.post(
    "/run-optimization", 
    status_code=202
)
def run_optimization_task(
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
) -> Any:
        # CHAMA A FUNÇÃO DE LÓGICA
        run = optimization_logic.create_optimization_run(db)
    
        # Adiciona a tarefa ao background
        background_tasks.add_task(run_optimization_background, run.id)
        
        return {
            "message": "Otimização iniciada com sucesso.",
            "detail": "O processo está sendo executado em segundo plano.",
            "run_id": run.id
        }

@router.get("/status/latest")
def get_latest_optimization_status(db: Session = Depends(get_db)):

    return optimization_logic.get_latest_optimization_status(db)

@router.get("/results/latest")
def get_latest_optimization_results(db: Session = Depends(get_db)):
    """ Retorna os resultados da última execução CONCLUÍDA. """
    return optimization_logic.get_latest_optimization_results(db)

@router.get(
    "/download/worker/{user_id}/run/{run_id}",
    response_class=StreamingResponse
)
def download_worker_schedule(
    user_id: int,
    run_id: int,
    db: Session = Depends(get_db)
):

    return optimization_logic.generate_worker_schedule_excel(
        db=db, user_id=user_id, run_id=run_id
    )