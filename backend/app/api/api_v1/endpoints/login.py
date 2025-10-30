from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordRequestForm 

from .... schemas.token import Token 

from .... core import security
from .... dependencies import get_db
from .... crud import crud_user

router = APIRouter()

@router.post("/token", response_model=Token) 
def login_for_access_token(

    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud_user.authenticate_user(
        db, 
        username=form_data.username, 
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_data = {"sub": user.username}
    access_token = security.create_access_token(data=access_token_data)

    return {"access_token": access_token, "token_type": "bearer"}