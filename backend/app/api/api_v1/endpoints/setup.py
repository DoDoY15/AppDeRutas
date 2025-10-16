
from fastapi import APIRouter, Depends, UploadFile, File , HTTPException
from sqlalchemy.orm import Session
from .... import schemas, security, crud , dependencies
from .... dependencies import get_db , require_admin_user
from .... crud import crud_user
from .... crud import crud_pos

router = APIRouter()

@router.post("/setup",)
def setup_system(
    users_file: UploadFile = File(..., description= "Excel file with users data"),
    pos_file: UploadFile = File(..., description= "Excel file with points of sale data"),
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(security.require_admin_user)
): 
    try:

        users_count = crud_user.process_and_load_users(db, users_file)
        pos_count = crud_pos.process_and_load_pos(db, pos_file)

        db.commit()

        return {"message": "Setup completed successfully","details": f"{users_count} users and {pos_count} points of sale added."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar o ficheiro de utilizadores: {str(e)}")