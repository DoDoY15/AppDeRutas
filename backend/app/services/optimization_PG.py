from sqlalchemy.orm import Session
from sqlalchemy.orm import Session, joinedload
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
    """ 
    Retorna os resultados da última execução CONCLUÍDA,
    incluindo a sequência de visitas por dia para a tabela.
    """
    
    latest_run = db.query(OptimizationRun).filter(
        OptimizationRun.status == OptimizationStatus.COMPLETED
    ).order_by(OptimizationRun.id.desc()).first()

    if not latest_run:
        raise HTTPException(status_code=404, detail="Nenhum resultado de otimização concluído encontrado.")

    # --- Métricas Globais (para o Dashboard) ---
    dashboard_data = {
        "run_id": latest_run.id,
        "total_pdvs_assigned": latest_run.total_pdvs_assigned,
        "total_pdvs_unassigned": latest_run.total_pdvs_unassigned,
        "created_at": latest_run.created_at,
    }

    # --- Dados da Tabela (com Sequência) ---
    
    # 1. Busca os Planos Semanais E carrega os Usuários
    worker_plans = db.query(WeeklyPlan).filter(
        WeeklyPlan.optimization_run_id == latest_run.id
    ).options(
        joinedload(WeeklyPlan.user) # Carrega o usuário junto (JOIN)
    ).all()
    
    # 2. Busca TODAS as visitas desta execução (muito eficiente)
    all_visits = db.query(DailyVisit).filter(
        DailyVisit.optimization_run_id == latest_run.id
    ).options(
        joinedload(DailyVisit.point_of_stop) # Carrega o PDV junto (JOIN)
    ).order_by(
        DailyVisit.visit_date.asc(),
        DailyVisit.visit_order.asc()
    ).all()
    
    # 3. Agrupa as visitas por usuário para facilitar
    visits_by_user = {}
    for visit in all_visits:
        if visit.user_id not in visits_by_user:
            visits_by_user[visit.user_id] = []
        visits_by_user[visit.user_id].append(visit)

    # 4. Constrói a resposta da tabela
    table_data = []
    for plan in worker_plans:
        user_data = { "full_name": plan.user.full_name }
        
        # --- LÓGICA DA SEQUÊNCIA (O que você pediu) ---
        sequencia_por_dia = {
            "Segunda": [], # (Dia 1)
            "Terça": [],   # (Dia 2)
            "Quarta": [],  # (Dia 3)
            "Quinta": [],  # (Dia 4)
            "Sexta": [],   # (Dia 5)
        }
        
        user_visits = visits_by_user.get(plan.user_id, [])
        
        for visit in user_visits:
            # .weekday() retorna 0 para Segunda, 1 para Terça...
            day_index = visit.visit_date.weekday() 
            pdv_name = visit.point_of_stop.name if visit.point_of_stop else "PDV Desconhecido"
            
            if day_index == 0:
                sequencia_por_dia["Segunda"].append(pdv_name)
            elif day_index == 1:
                sequencia_por_dia["Terça"].append(pdv_name)
            elif day_index == 2:
                sequencia_por_dia["Quarta"].append(pdv_name)
            elif day_index == 3:
                sequencia_por_dia["Quinta"].append(pdv_name)
            elif day_index == 4:
                sequencia_por_dia["Sexta"].append(pdv_name)
        # --- FIM DA LÓGICA ---

        table_data.append({
            "id": plan.id,
            "user_id": plan.user_id, # <-- DADO NOVO (usuario_id)
            "user": user_data,
            "horas_semanais_estimadas": (plan.user.weekly_working_seconds / 3600) or 0, 
            "total_pos_assigned": plan.total_pos_assigned,
            "download_link": f"/api/v1/optimize/download/worker/{plan.user_id}/run/{latest_run.id}",
            "sequencia": sequencia_por_dia # <-- DADO NOVO (Secuencia)
        })
        
    return {"dashboard": dashboard_data, "table": table_data}
# ======================================================================
# LÓGICA PARA: GET /Download
# ======================================================================
def generate_worker_schedule_excel(db: Session, user_id: int, run_id: int) -> StreamingResponse:
    """
    Consulta o DB e gera um arquivo Excel em memória para download,
    incluindo os novos dados de tempo de chegada/saída.
    """
    
    # 1. Consultar os Dados (A "Agenda" do DB)
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
    worker_name = visits_data[0].User.full_name
    
    total_time_acumulado_seg = 0
    total_travel_time_seg = 0

    for visit, user, pdv in visits_data:
        
        # --- CÁLCULO DE ACUMULADOS ---
        travel_time_min = (visit.duration_from_previous_seconds or 0) / 60
        visit_time_min = (pdv.visit_duration_seconds or 0) / 60
        
        total_travel_time_seg += (visit.duration_from_previous_seconds or 0)
        total_time_acumulado_seg += (visit.duration_from_previous_seconds or 0) + (pdv.visit_duration_seconds or 0)

        data_for_excel.append({
            "Data da Visita": visit.visit_date.strftime("%Y-%m-%d"),
            "Dia da Semana": visit.visit_date.strftime("%A"),
            "Ordem da Visita": visit.visit_order,
            "Trabalhador": user.full_name,
            "PDV (Loja)": pdv.name,
            "Endereço": pdv.address,
            
            # --- NOVAS COLUNAS REQUERIDAS ---
            "Tempo de Deslocamento (min)": round(travel_time_min, 1),
            "Hora de Chegada Estimada": visit.estimated_arrival_time,
            "Duração da Visita (min)": round(visit_time_min, 1),
            "Hora de Saída Estimada": visit.estimated_departure_time,
            "Tempo de Viagem Acumulado (min)": round(total_travel_time_seg / 60, 1),
            "Tempo Total Acumulado (min)": round(total_time_acumulado_seg / 60, 1)
            # --- FIM DAS NOVAS COLUNAS ---
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