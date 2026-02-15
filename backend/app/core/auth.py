"""
JWT Authentication Module

Maneja la creación y validación de tokens JWT para autenticación.
Se utiliza HS256 con expiración de 24 horas.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models import User
from sqlalchemy import select


def create_access_token(user_id: int) -> str:
    """
    Crea un token JWT con expiración de 24 horas.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Token JWT como string
    """
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow(),
    }
    
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return token


def decode_token(token: str) -> Optional[int]:
    """
    Decodifica y valida un token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        user_id si es válido, None si no lo es
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: int = int(payload.get("sub"))
        return user_id
    except (ExpiredSignatureError, JWTError, ValueError, TypeError):
        return None


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependencia que valida el token JWT y retorna el usuario.
    
    Args:
        authorization: Header Authorization: "Bearer <token>"
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException 401: Token inválido o expirado
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer token del header "Bearer <token>"
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de Authorization inválido. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = decode_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario de la base de datos
    user = db.scalar(select(User).where(User.id == user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_admin_user(
    user: User = Depends(get_current_user),
) -> User:
    """Guard de admin basado en el estado persistido (is_admin) del usuario."""

    if not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "forbidden",
                "detail": "Requiere permisos de administrador",
                "code": "ADMIN_REQUIRED",
            },
        )
    return user
