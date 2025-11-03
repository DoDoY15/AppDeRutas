
from fastapi import APIRouter, Depends, UploadFile, File , HTTPException
from sqlalchemy.orm import Session
from .... core import security
from .... schemas import user as schemas
from ....schemas import point_of_stop as pos_schemas
from ....dependencies import get_db , require_admin_user
from .... crud import crud_user
from .... crud import crud_pos

router = APIRouter()

@router.post("/users/upload")
def upload_users(
    users_file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        # A função agora retorna uma tupla
        criados, atualizados = crud_user.process_and_load_users(db, users_file)
        db.commit()
        return {
            "message": "Arquivo de usuários processado com sucesso.",
            "details": f"{criados} usuários criados, {atualizados} usuários atualizados."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {str(e)}")

@router.post("/pos/upload")
def upload_pos(
    pos_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # A função agora retorna uma tupla
        criados, atualizados = crud_pos.process_and_load_pos(db, pos_file)
        db.commit()
        return {
            "message": "Arquivo de PDVs processado com sucesso.",
            "details": f"{criados} PDVs criados, {atualizados} PDVs atualizados."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {str(e)}")