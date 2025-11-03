from sqlalchemy.orm import Session
from typing import Any, Dict
from fastapi import HTTPException
from app.db.models import OptimizationRun, OptimizationStatus, WeeklyPlan, User
from fastapi.responses import StreamingResponse
from app.db.models import DailyVisit, PointOfStop
import pandas as pd
import io

# ======================================================================
# LÓGICA PARA: POST /run-optimization
# ======================================================================
def create_optimization_run(db: Session) -> OptimizationRun:
    """
    Cria uma nova entrada OptimizationRun com status PENDING
    e a retorna.
    """
    run = OptimizationRun(status=OptimizationStatus.PENDING)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

# ======================================================================
# LÓGICA PARA: GET /status/latest
# ======================================================================
def get_latest_optimization_status(db: Session) -> Dict[str, Any]:
    """ Retorna o status da última execução iniciada. """
    
    latest_run = db.query(OptimizationRun).order_by(OptimizationRun.id.desc()).first()
    
    if not latest_run:
        return {"status": "NOT_FOUND"}
        
    return {
        "status": latest_run.status, 
        "run_id": latest_run.id, 
        "created_at": latest_run.created_at,
        "total_pdvs_assigned": latest_run.total_pdvs_assigned,
        "total_pdvs_unassigned": latest_run.total_pdvs_unassigned
    }

# ======================================================================
# LÓGICA PARA: GET /results/latest
# ======================================================================
def get_latest_optimization_results(db: Session) -> Dict[str, Any]:
    """ Retorna os resultados da última execução CONCLUÍDA. """
    
    latest_run = db.query(OptimizationRun).filter(
        OptimizationRun.status == OptimizationStatus.COMPLETED
    ).order_by(OptimizationRun.id.desc()).first()

    if not latest_run:
        raise HTTPException(status_code=404, detail="Nenhum resultado de otimização concluído encontrado.")

    dashboard_data = {
        "run_id": latest_run.id,
        "total_pdvs_assigned": latest_run.total_pdvs_assigned,
        "total_pdvs_unassigned": latest_run.total_pdvs_unassigned,
        "created_at": latest_run.created_at,
    }

    worker_plans = db.query(WeeklyPlan).filter(
        WeeklyPlan.optimization_run_id == latest_run.id
    ).join(User).all() 

    table_data = []
    for plan in worker_plans:
        user_data = { "full_name": plan.user.full_name }

        table_data.append({
            "id": plan.id, 
            "user": user_data,
            "horas_semanais_estimadas": (plan.user.weekly_working_seconds / 3600) or 0, 
            "total_pdvs_assigned": plan.total_pos_assigned,
            # (O prefixo /api/v1 vem do seu roteador principal)
            "download_link": f"/api/v1/optimize/download/worker/{plan.user_id}/run/{latest_run.id}"
        })
        
    return {"dashboard": dashboard_data, "table": table_data}

def generate_worker_schedule_excel(db: Session, user_id: int, run_id: int) -> StreamingResponse:

    #  Consultar os Dados (A "Agenda" do DB)
    visits_query = db.query(
        DailyVisit, User, PointOfStop
    ).join(
        User, DailyVisit.user_id == User.id
    ).join(
        PointOfStop, DailyVisit.point_of_stop_id == PointOfStop.id
    ).filter(
        DailyVisit.user_id == user_id,
        DailyVisit.optimization_run_id == run_id
    ).order_by(
        DailyVisit.visit_date.asc(),
        DailyVisit.visit_order.asc()
    )
    
    visits_data = visits_query.all()

    if not visits_data:
        raise HTTPException(
            status_code=404, 
            detail="Nenhuma agenda encontrada para este trabalhador e execução."
        )

    # 2. Formatar os Dados para o Excel
    data_for_excel = []
    worker_name = visits_data[0].User.full_name # Pega o nome do primeiro registro

    for visit, user, pdv in visits_data:
        data_for_excel.append({
            "Data da Visita": visit.visit_date.strftime("%Y-%m-%d"),
            "Dia da Semana": visit.visit_date.strftime("%A"),
            "Ordem da Visita": visit.visit_order,
            "Trabalhador": user.full_name,
            "PDV (Loja)": pdv.name,
            "Endereço": pdv.address,
            "Cidade": pdv.city,
            "Duração Estimada (min)": (pdv.visit_duration_seconds / 60),
            "ID do PDV (Externo)": pdv.external_id,
        })

    # 3. Gerar o Arquivo Excel em Memória
    df = pd.DataFrame(data_for_excel)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Plano - {worker_name}')
    output.seek(0)

    # 4. Preparar a Resposta
    filename = f"plano_run_{run_id}_worker_{user_id}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }

    # 5. Retornar o StreamingResponse
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )