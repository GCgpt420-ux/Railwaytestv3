from app.db.models import AttemptFeedback, Question, QuestionChoice
from sqlalchemy.orm import Session


def generate_feedback_phase1(feedback: AttemptFeedback, db: Session) -> dict:
    """
    Fase 1 - Rule-based feedback generator (sin LLM).
    Estrategia:
    1. Si respuesta correcta: feedback positivo variado
    2. Si incorrecta: hint basado en el tema + text de la opción correcta
    """
    
    # Obtener question y correcta choice
    question = db.query(Question).get(feedback.question_id)
    correct_choice = db.query(QuestionChoice).filter(
        QuestionChoice.question_id == feedback.question_id,
        QuestionChoice.is_correct == True
    ).first()
    
    if not question or not correct_choice:
        return {"explanation": "No se pudo generar feedback.", "source": "rule_based_phase1"}
    
    if feedback.is_correct:
        # Feedback positivo variado
        positive_messages = [
            "¡Excelente! Respuesta correcta.",
            "¡Muy bien! Demostraste dominar este concepto.",
            "¡Correcto! Vas muy bien.",
            "¡Perfecto! Ese es el camino.",
            "¡Súper! Respuesta acertada.",
        ]
        
        # Seleccionar basado en alguna variable (p.ej: streak, etc)
        msg = positive_messages[feedback.attempt_id % len(positive_messages)]
        
        return {
            "explanation": msg,
            "is_correct": True,
            "source": "rule_based_phase1"
        }
    
    else:
        # Feedback negativo con hint
        # Mostrar la respuesta correcta y un hint genérico
        topic = question.topic.code if question.topic else "general"
        
        feedback_messages = {
            "ALG": "Recuerda: este tema trata sobre Álgebra. Revisa las propiedades y operaciones algebraicas.",
            "GEO": "Tip: en Geometría, considera las propiedades de figuras y ángulos.",
            "LECT": "Sugerencia: en Lectura, releer el párrafo clave ayuda.",
            "CIEN": "Consejo: en Ciencias, piensa en los procesos y reacciones.",
            "HIST": "Tip: en Historia, el contexto temporal es crucial.",
        }
        
        hint = feedback_messages.get(topic, "Revisa el concepto y intenta nuevamente.")
        
        return {
            "explanation": f"Respuesta incorrecta. {hint}\n\nRespuesta correcta: {correct_choice.label}. {correct_choice.text}",
            "is_correct": False,
            "correct_choice_id": correct_choice.id,
            "correct_choice_label": correct_choice.label,
            "source": "rule_based_phase1"
        }


def generate_feedback(feedback: AttemptFeedback, db: Session) -> dict:
    """
    Main feedback generator.
    
    Por ahora: fase 1 (reglas).
    Futuro: agregar LLM en fase 2.
    """
    return generate_feedback_phase1(feedback, db)

