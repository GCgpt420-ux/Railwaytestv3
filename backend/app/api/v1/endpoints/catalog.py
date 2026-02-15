"""
Catalog endpoints - Exámenes, asignaturas, temas
Sin autenticación requerida (catálogo público)
"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

from app.db.session import get_db
from app.db.models import Exam, Subject, Topic
from app.core.exceptions import not_found

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/exams/")
def get_exams(db: Session = Depends(get_db)):
    """
    GET /api/v1/catalog/exams/
    
    Obtiene lista de exámenes disponibles.
    
    Returns:
    [
        {
            "exam_id": 1,
            "code": "PAES",
            "title": "PAES 2024",
            "subjects": [...]
        }
    ]
    """
    exams = db.scalars(select(Exam)).all()
    
    result = []
    for exam in exams:
        subjects = db.scalars(
            select(Subject).where(Subject.exam_id == exam.id)
        ).all()
        
        result.append({
            "exam_id": exam.id,
            "code": exam.code,
            "name": exam.name,
            "subjects": [
                {
                    "subject_id": s.id,
                    "subject_code": s.code,
                    "name": s.name
                }
                for s in subjects
            ]
        })
    
    return result


@router.get("/subjects/")
def get_subjects(exam_id: int = Query(...), db: Session = Depends(get_db)):
    """
    GET /api/v1/catalog/subjects/?exam_id=1
    
    Obtiene asignaturas de un examen.
    
    Query params:
    - exam_id: ID del examen
    
    Returns:
    [
        {
            "subject_id": 1,
            "subject_code": "MATH1",
            "name": "Matemática 1",
            "topics": [...]
        }
    ]
    """
    exam = db.scalar(select(Exam).where(Exam.id == exam_id))
    if not exam:
        raise not_found("exam_not_found", f"Exam {exam_id} not found")
    
    subjects = db.scalars(
        select(Subject).where(Subject.exam_id == exam_id)
    ).all()
    
    result = []
    for subject in subjects:
        topics = db.scalars(
            select(Topic).where(Topic.subject_id == subject.id)
        ).all()
        
        result.append({
            "subject_id": subject.id,
            "subject_code": subject.code,
            "name": subject.name,
            "topics": [
                {
                    "topic_id": t.id,
                    "topic_code": t.code,
                    "name": t.name
                }
                for t in topics
            ]
        })
    
    return result


@router.get("/topics/")
def get_topics(subject_id: int = Query(...), db: Session = Depends(get_db)):
    """
    GET /api/v1/catalog/topics/?subject_id=1
    
    Obtiene temas de una asignatura.
    
    Query params:
    - subject_id: ID de la asignatura
    
    Returns:
    [
        {
            "topic_id": 1,
            "topic_code": "ALGEBRA",
            "name": "Álgebra"
        }
    ]
    """
    subject = db.scalar(select(Subject).where(Subject.id == subject_id))
    if not subject:
        raise not_found("subject_not_found", f"Subject {subject_id} not found")
    
    topics = db.scalars(
        select(Topic).where(Topic.subject_id == subject_id)
    ).all()
    
    return [
        {
            "topic_id": t.id,
            "topic_code": t.code,
            "name": t.name
        }
        for t in topics
    ]
