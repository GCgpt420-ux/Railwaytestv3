from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import (
    User, Attempt, Subject, Topic, Exam
)
from app.core.exceptions import not_found, bad_request
from app.core.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}/stats")
def user_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "forbidden",
                "detail": "user_id no coincide con el token",
                "code": "IDOR_BLOCKED",
            },
        )
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise not_found("user", f"user_id={user_id}")

    exam = db.scalar(select(Exam).where(Exam.code == "PAES"))
    if not exam:
        raise bad_request("exam_not_seeded", "PAES exam not initialized. Run seed_paes.py")

    subjects = db.scalars(
        select(Subject)
        .where(Subject.exam_id == exam.id)
        .order_by(Subject.id.asc())
    ).all()

    subject_ids = [s.id for s in subjects]
    topic_rows = db.execute(
        select(Topic.id, Topic.code, Topic.name, Topic.subject_id)
        .where(Topic.subject_id.in_(subject_ids) if subject_ids else False)
        .order_by(Topic.id.asc())
    ).all()

    attempt_rows = db.execute(
        select(
            Attempt.subject_id,
            Attempt.topic_id,
            Attempt.status,
            Attempt.total_questions,
            Attempt.correct_count,
            Attempt.completed_at,
        )
        .where(Attempt.user_id == user_id)
    ).all()

    topic_stats = {}
    total_questions = 0
    total_correct = 0

    for row in attempt_rows:
        total_questions += int(row.total_questions or 0)
        total_correct += int(row.correct_count or 0)

        if not row.topic_id:
            continue

        stats = topic_stats.setdefault(
            row.topic_id,
            {"questions": 0, "correct": 0, "completed_at": None},
        )

        stats["questions"] += int(row.total_questions or 0)
        stats["correct"] += int(row.correct_count or 0)

        if row.status == "completed" and row.completed_at:
            if not stats["completed_at"] or row.completed_at > stats["completed_at"]:
                stats["completed_at"] = row.completed_at

    overall_accuracy = (
        round((total_correct / total_questions) * 100, 2) if total_questions else 0
    )

    topics_by_subject = {}
    for t in topic_rows:
        topics_by_subject.setdefault(t.subject_id, []).append(t)

    completed_subjects = 0
    subjects_payload = []

    for subject in subjects:
        topics_payload = []
        subject_topics = topics_by_subject.get(subject.id, [])
        subject_completed = True if subject_topics else False

        for topic in subject_topics:
            stats = topic_stats.get(topic.id, {"questions": 0, "correct": 0, "completed_at": None})
            questions = stats["questions"]
            correct = stats["correct"]
            accuracy = round((correct / questions) * 100, 2) if questions else 0
            completed_at = stats["completed_at"]

            if not completed_at:
                subject_completed = False

            topics_payload.append(
                {
                    "topic_code": topic.code,
                    "accuracy": accuracy,
                    "completed_at": completed_at.isoformat() if completed_at else None,
                }
            )

        if subject_completed:
            completed_subjects += 1

        subjects_payload.append(
            {
                "subject_code": subject.code,
                "subject_name": subject.name,
                "topics": topics_payload,
            }
        )

    return {
        "user_id": user_id,
        "total_subjects": len(subjects),
        "completed_subjects": completed_subjects,
        "overall_accuracy": overall_accuracy,
        "subjects": subjects_payload,
    }



