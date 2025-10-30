
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
    users_file: UploadFile = File(..., description= "Excel file with users data"), 
    db: Session = Depends(get_db),
    # current_admin: schemas.User = Depends(require_admin_user)
):
    try:

        users_count = crud_user.process_and_load_users(db, users_file)

        db.commit()

        return {"message": "Setup completed successfully","details": f"{users_count} users ."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar o ficheiro de utilizadores: {str(e)}")

@router.post("/pos/upload")
def upload_pos(
    pos_file: UploadFile = File(..., description= "Excel file with points of sale data"),
    db: Session = Depends(get_db)
    # current_admin: schemas.User = Depends(require_admin_user)
):
    try:
        pos_count = crud_pos.process_and_load_pos(db,pos_file)
        db.commit()

        return {"message": "POS file processed successfully", "details": f"{pos_count} points of sale added."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar o ficheiro de PDVs: {str(e)}")