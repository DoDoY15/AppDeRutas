from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    BackgroundTasks 
)
from sqlalchemy.orm import Session
from typing import Any

from app.dependencies import get_db 
from app.services.routeGeneration.calc import generate_and_save_schedules
from app.db.models import OptimizationRun, OptimizationStatus, weaklyPlan, User, DailyVisit


router = APIRouter()
@router.post(
    "/run-optimization", 
    status_code=202
)
def run_optimization_task(
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
) -> Any:
        run = OptimizationRun(status=OptimizationStatus.PENDING)
        db.add(run)
        db.commit()
        db.refresh(run)

        background_tasks.add_task(generate_and_save_schedules, db, run.id)
        
        return {
            "message": "Otimização iniciada com sucesso.",
            "detail": "O processo está sendo executado em segundo plano."
        }
@router.get("/status/latest")
def get_latest_optimization_status(db: Session = Depends(get_db)):

    latest_run = db.query(OptimizationRun).order_by(OptimizationRun.id.desc()).first()
    if not latest_run:
        return {"status": "NOT_FOUND"}
    return {"status": latest_run.status, "run_id": latest_run.id, "created_at": latest_run.created_at}
@router.get("/results/latest")
def get_latest_optimization_results(db: Session = Depends(get_db)):

    latest_run = db.query(OptimizationRun).filter(
        OptimizationRun.status == OptimizationStatus.COMPLETED
    ).order_by(OptimizationRun.id.desc()).first()

    if not latest_run:

        raise HTTPException(status_code=404, detail="Nenhum resultado de otimização concluído encontrado.")

    dashboard_data = {
        "total_pdvs_assigned": latest_run.total_pdvs_assigned,
        "total_pdvs_unassigned": latest_run.total_pdvs_unassigned,
        "created_at": latest_run.created_at,
    }

    worker_plans = db.query(weaklyPlan).filter(
        weaklyPlan.optimization_run_id == latest_run.id
    ).join(User).all() 

    table_data = []
    for plan in worker_plans:

        user_data = {
            "full_name": plan.user.full_name 
        }

        table_data.append({
            "id": plan.id, 
            "user": user_data,
            "horas_semanais_estimadas": (plan.user.weakly_working_seconds / 3600) or 0, 
            "total_pdvs_assigned": plan.total_pdvs_assigned,
            
            "download_link": f"/api/v1/optimize/download/worker/{plan.user_id}/run/{latest_run.id}"
        })
    return {"dashboard": dashboard_data, "table": table_data}