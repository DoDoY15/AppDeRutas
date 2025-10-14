from fastapi import Depends, HTTPException, status
from . import models

# Função temporária que simula um utilizador logado
def get_current_user() -> models.User:
    user = models.User(
        id=1,
        username="testadmin",
        role=models.UserRole.ADMIN, # Mude para .USER para testar o erro 403
        hashed_password="fake"
    )
    return user

# ESTA é a função que queremos usar para proteger o endpoint
def require_admin_user(current_user: models.User = Depends(get_current_user)):
    """
    Verifica se o utilizador atual é um admin. Se não for,
    levanta uma exceção HTTP 403 (Forbidden).
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Requer privilégios de administrador."
        )
    return current_user