from fastapi import APIRouter, Depends, UploadFile, File 
from sqlalchemy.orm import Session

from ... import schemas
from ... dependencies import get_db
 # import adm dependecy

router = APIRouter()

router.post("/setup", tags=["Admin"])

def setup_system(
    users_file: UploadFile = File(..., description= "Excel file with users data"),
    pos_file: UploadFile = File(..., description= "Excel file with points of sale data"),
    db: Session = Depends(get_db),
    current_admin: schemas.User = Depends(security.require_admin_user)
):