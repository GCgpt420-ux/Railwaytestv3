from datetime import datetime
from typing import Optional, Union
import logging
import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import not_found, bad_request
from app.core.auth import get_current_user
from app.db.session import get_db
from app.db.models import Topic, Question, QuestionChoice, Exam, Subject, Attempt, AttemptFeedback, User
from app.schemas.quiz import QuestionOut, AnswerIn, AnswerOut, TopicCompletedOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/next-question", response_model=Union[QuestionOut, TopicCompletedOut])
def next_question(
    attempt_id: Optional[int] = None,
    topic_code: str = "ALG",
    subject_code: str = "M1",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    logger.info(
        "User %s requesting next question | Subject: %s | Topic: %s",
        user_id,
        subject_code,
        topic_code,
    )

    exam = db.scalar(select(Exam).where(Exam.code == settings.PAES_CODE))
    if not exam:
        raise bad_request(
            "exam_not_seeded",
            f"{settings.PAES_CODE} exam no inicializado. Ejecutar seed_paes.py",
        )

    subject = db.scalar(
        select(Subject).where(Subject.exam_id == exam.id, Subject.code == subject_code)
    )
    if not subject:
        raise not_found("subject", f"subject_code={subject_code} en exam={exam.code}")

    topic = db.scalar(
        select(Topic).where(Topic.subject_id == subject.id, Topic.code == topic_code)
    )
    if not topic:
        raise not_found("topic", f"topic_code={topic_code} en subject_code={subject_code}")

    if attempt_id is not None:
        attempt = db.get(Attempt, attempt_id)
        if not attempt or attempt.user_id != user_id:
            raise not_found("attempt", f"attempt_id={attempt_id}")
        if (
            attempt.exam_id != exam.id
            or attempt.subject_id != subject.id
            or attempt.topic_id != topic.id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "bad_request",
                    "detail": "attempt_id no coincide con subject/topic del request",
                    "code": "ATTEMPT_MISMATCH",
                },
            )
    else:
        attempt = db.scalar(
            select(Attempt)
            .where(
                Attempt.user_id == user_id,
                Attempt.exam_id == exam.id,
                Attempt.subject_id == subject.id,
                Attempt.topic_id == topic.id,
                Attempt.status == "in_progress",
            )
            .order_by(Attempt.id.desc())
        )

    answered_question_ids = set()
    if attempt:
        answered_question_ids = set(
            db.scalars(
                select(AttemptFeedback.question_id).where(AttemptFeedback.attempt_id == attempt.id)
            ).all()
        )

    question = db.scalar(
        select(Question)
        .where(
            Question.topic_id == topic.id,
            Question.is_active == True,  # noqa: E712
            Question.id.not_in(answered_question_ids) if answered_question_ids else True,
        )
        .order_by(func.random())
    )

    if not question:
        if not attempt:
            raise bad_request("no_attempt", "No active attempt found for this topic")

        attempt.status = "completed"
        attempt.completed_at = datetime.utcnow()

        total = attempt.total_questions or 0
        correct = attempt.correct_count or 0

        if total == 0:
            logger.warning("Attempt %s has no questions answered", attempt.id)
            raise bad_request(
                "no_questions_answered",
                "Cannot complete topic without answering at least one question",
            )

        score_percentage = int((correct / total) * 100)
        score_paes = int((correct / total) * 1000)

        attempt.score = score_paes
        db.commit()

        logger.info(
            "Topic completed | User: %s | Score: %s/%s (%s%%)",
            user_id,
            correct,
            total,
            score_percentage,
        )

        return {
            "kind": "topic_completed",
            "message": "¡Tema completado!",
            "attempt_id": attempt.id,
            "status": attempt.status,
            "total_questions": total,
            "correct_count": correct,
            "score_percentage": score_percentage,
            "score_paes": score_paes,
            "score": score_paes,
        }

    choices = db.scalars(
        select(QuestionChoice).where(QuestionChoice.question_id == question.id)
    ).all()
    random.shuffle(choices)

    logger.debug("Serving question %s to user %s", question.id, user_id)

    return {
        "kind": "question",
        "question_id": question.id,
        "prompt": question.prompt,
        "topic": topic.code,
        "reading_text": question.reading_text,
        "choices": [
            {"id": choice.id, "label": choice.label, "text": choice.text}
            for choice in choices
        ],
    }

@router.post("/answer", response_model=AnswerOut)
def submit_answer(
    payload: AnswerIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.user_id is not None and payload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "forbidden",
                "detail": "user_id no coincide con el token",
                "code": "IDOR_BLOCKED",
            },
        )
    user_id = current_user.id
    logger.info(
        "User %s answering | Question: %s | Choice: %s",
        user_id,
        payload.question_id,
        payload.selected_choice_id,
    )

    question = db.get(Question, payload.question_id)
    if not question:
        raise not_found("question", "Question does not exist")

    choice = db.get(QuestionChoice, payload.selected_choice_id)
    if not choice or choice.question_id != payload.question_id:
        raise bad_request("invalid_choice", "Selected choice does not belong to this question")

    exam = db.scalar(select(Exam).where(Exam.code == settings.PAES_CODE))
    if not exam:
        raise bad_request(
            "exam_not_seeded",
            f"{settings.PAES_CODE} exam no inicializado. Ejecutar seed_paes.py",
        )

    subject = db.scalar(
        select(Subject).where(Subject.exam_id == exam.id, Subject.code == payload.subject_code)
    )
    if not subject:
        raise not_found("subject", f"subject_code={payload.subject_code} en exam={exam.code}")

    topic = db.scalar(
        select(Topic).where(Topic.subject_id == subject.id, Topic.code == payload.topic_code)
    )
    if not topic:
        raise not_found("topic", f"topic_code={payload.topic_code} en subject_code={payload.subject_code}")

    is_correct = bool(choice.is_correct)

    attempt = db.scalar(
        select(Attempt)
        .where(
            Attempt.user_id == user_id,
            Attempt.exam_id == exam.id,
            Attempt.subject_id == subject.id,
            Attempt.topic_id == topic.id,
            Attempt.status == "in_progress",
        )
        .order_by(Attempt.id.desc())
    )
    if not attempt:
        attempt = Attempt(
            user_id=user_id,
            exam_id=exam.id,
            subject_id=subject.id,
            topic_id=topic.id,
            status="in_progress",
            started_at=datetime.utcnow(),
            total_questions=0,
            correct_count=0,
        )
        db.add(attempt)
        db.flush()

    feedback_text = "¡Correcto!" if is_correct else "Incorrecto (por ahora sin IA)."

    def _attempt_has_remaining_questions(attempt_id: int) -> bool:
        answered_ids = db.scalars(
            select(AttemptFeedback.question_id).where(AttemptFeedback.attempt_id == attempt_id)
        ).all()
        answered_set = set(answered_ids)
        remaining = db.scalar(
            select(Question.id)
            .where(
                Question.topic_id == topic.id,
                Question.is_active == True,  # noqa: E712
                Question.id.not_in(answered_set) if answered_set else True,
            )
            .limit(1)
        )
        return remaining is not None

    def _finalize_attempt(attempt: Attempt) -> None:
        if attempt.status == "completed":
            return
        attempt.status = "completed"
        attempt.completed_at = datetime.utcnow()
        total = attempt.total_questions or 0
        correct = attempt.correct_count or 0
        if total > 0:
            score_paes = int((correct / total) * 1000)
            attempt.score = score_paes

    # SNIPPET 2: Deduplicacion (evitar respuestas duplicadas)
    existing_feedback = db.scalar(
        select(AttemptFeedback).where(
            AttemptFeedback.attempt_id == attempt.id,
            AttemptFeedback.question_id == payload.question_id,
        )
    )
    if existing_feedback:
        logger.info(
            "Duplicate answer detected | Question: %s | Returning cached feedback",
            payload.question_id,
        )

        is_finished = False
        if not _attempt_has_remaining_questions(attempt.id):
            _finalize_attempt(attempt)
            db.commit()
            is_finished = True

        return {
            "attempt_id": attempt.id,
            "feedback_id": existing_feedback.id,
            "is_correct": existing_feedback.is_correct,
            "feedback_text": existing_feedback.feedback_text,
            "is_attempt_finished": is_finished or attempt.status == "completed",
            "ai_payload": existing_feedback.ai_payload or {},
        }
    fb = AttemptFeedback(
        attempt_id=attempt.id,
        question_id=payload.question_id,
        selected_choice_id=payload.selected_choice_id,
        is_correct=is_correct,
        feedback_text=feedback_text,
        ai_payload={},  # placeholder: aquí va resultado de OpenAI después
    )
    db.add(fb)

    attempt.total_questions = (attempt.total_questions or 0) + 1
    if is_correct:
        attempt.correct_count = (attempt.correct_count or 0) + 1

    db.flush()

    is_finished = False
    if not _attempt_has_remaining_questions(attempt.id):
        _finalize_attempt(attempt)
        is_finished = True

    db.commit()

    logger.info(
        "Answer recorded | Result: %s | Progress: %s/%s",
        "✓ correct" if is_correct else "✗ incorrect",
        attempt.correct_count,
        attempt.total_questions,
    )

    return {
        "attempt_id": attempt.id,
        "feedback_id": fb.id,
        "is_correct": is_correct,
        "feedback_text": feedback_text,
        "is_attempt_finished": is_finished,
        "ai_payload": {},
    }
