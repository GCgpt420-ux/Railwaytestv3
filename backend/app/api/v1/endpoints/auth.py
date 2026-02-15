"""
Auth endpoints - Login MVP (sin validación de credenciales)

Soporta:
- Email: POST /login {"email": "demo@example.com"} → crea si no existe
- User ID: POST /login {"user_id": 1} → busca usuario existente
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import User
from app.core.exceptions import bad_request
from app.core.auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    """Retorna datos del usuario actual para rehidratar la sesión del frontend."""

    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "is_admin": bool(getattr(current_user, "is_admin", False)),
    }


@router.post("/login")
def login(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    POST /api/v1/auth/login
    
    Login MVP - Flexible: acepta email O user_id
    
    Opción 1 (Email - Auto-create):
    {
        "email": "demo@example.com",
        "name": "Demo User" (opcional)
    }
    → Busca por email, crea si no existe
    
    Opción 2 (User ID):
    {
        "user_id": 1
    }
    → Busca por ID, error si no existe
    
    Returns:
    {
        "access_token": "fake-token-{user_id}",
        "user_id": 1,
        "email": "demo@example.com",
        "name": "Demo User"
    }
    """
    user_id_input = request.get("user_id")
    email_input = request.get("email", "").strip()
    name_input = request.get("name", "").strip()
    
    user = None
    
    # RUTA 1: Buscar por user_id
    if user_id_input:
        user = db.scalar(select(User).where(User.id == user_id_input))
        if not user:
            raise bad_request(
                "user_not_found",
                f"User ID {user_id_input} not found"
            )
    
    # RUTA 2: Buscar/crear por email
    elif email_input:
        user = db.scalar(select(User).where(User.email == email_input))
        if not user:
            # Auto-create en MVP mode
            user = User(
                email=email_input,
                name=name_input or email_input.split("@")[0],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    
    else:
        raise bad_request(
            "auth_required",
            "Must provide either 'email' or 'user_id'"
        )
    return {
        "access_token": create_access_token(user.id),
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "is_admin": bool(getattr(user, "is_admin", False)),
    }
