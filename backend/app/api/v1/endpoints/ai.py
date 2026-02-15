from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import AttemptFeedback
from app.services.ai_service import generate_feedback
from app.schemas.quiz import AIFeedbackOut
# importar schema de IA desde quiz.py

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/feedback/{feedback_id}", response_model=AIFeedbackOut)
# agregar response_model para validar respuesta de IA, por el momento no se usa ya que no tenemos la ia_service implementada
# Se agrego para un futuro cercano xd
def ai_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para obtener feedback generado por IA.
    
    Futuro: aquí se llamará al LLM para generar explicaciones personalizadas.
    Hoy: retorna feedback escrito basado en reglas predefinidas.
    """
    fb = db.scalar(select(AttemptFeedback).where(AttemptFeedback.id == feedback_id))
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return generate_feedback(fb, db)
