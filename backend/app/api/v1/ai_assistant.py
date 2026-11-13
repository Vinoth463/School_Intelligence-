
from fastapi import APIRouter, Depends, HTTPException
from groq import APIError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User
from app.models.student import Student
from app.models.subject import Subject
from app.models.classroom import Classroom
from app.models.examination import Examination
from app.models.academic_period import AcademicPeriod

from app.schemas.ai_assistant import (
    AcademicAssistantRequest,
    AcademicAssistantResponse,
)

from app.ai.academic_assistant_service import (
    ask_academic_assistant,
)
from app.ai.entity_resolution_service import (
    resolve_question_entities,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI Academic Assistant"],
)


@router.post(
    "/academic-assistant",
    response_model=AcademicAssistantResponse,
)
def academic_assistant(
    payload: AcademicAssistantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    resolved = resolve_question_entities(
        db=db,
        institution_id=institution_id,
        question=payload.question,
    )

    if resolved["clarification"]:
        raise HTTPException(
            status_code=400,
            detail=resolved["clarification"],
        )
    # Validate academic period.
    if payload.academic_period_id is not None:
        period_exists = db.scalar(
            select(AcademicPeriod.id).where(
                AcademicPeriod.id == payload.academic_period_id,
                AcademicPeriod.institution_id == institution_id,
            )
        )

        if period_exists is None:
            raise HTTPException(
                status_code=404,
                detail="Academic period not found for this institution.",
            )

    # Validate classroom.
    if payload.class_id is not None:
        class_exists = db.scalar(
            select(Classroom.id).where(
                Classroom.id == payload.class_id,
                Classroom.institution_id == institution_id,
            )
        )

        if class_exists is None:
            raise HTTPException(
                status_code=404,
                detail="Class not found for this institution.",
            )

    # Validate subject.
    if payload.subject_id is not None:
        subject_exists = db.scalar(
            select(Subject.id).where(
                Subject.id == payload.subject_id,
                Subject.institution_id == institution_id,
            )
        )

        if subject_exists is None:
            raise HTTPException(
                status_code=404,
                detail="Subject not found for this institution.",
            )

    # Validate student.
    if payload.student_id is not None:
        student_exists = db.scalar(
            select(Student.id).where(
                Student.id == payload.student_id,
                Student.institution_id == institution_id,
            )
        )

        if student_exists is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found for this institution.",
            )

    
    # Resolve the effective target examination ID.
    target_examination_id = (
        payload.target_examination_id
        if payload.target_examination_id is not None
        else resolved["target_examination_id"]
    )

    # Determine the effective academic period.
    effective_academic_period_id = (
        payload.academic_period_id
        if payload.academic_period_id is not None
        else resolved["academic_period_id"]
    )

    # Validate target examination.
    if target_examination_id is not None:
        examination = db.scalar(
            select(Examination).where(
                Examination.id == target_examination_id,
                Examination.institution_id == institution_id,
            )
        )

        if examination is None:
            raise HTTPException(
                status_code=404,
                detail="Target examination not found for this institution.",
            )

        # Ensure the target examination belongs to the effective period.
        if (
            effective_academic_period_id is not None
            and examination.academic_period_id
            != effective_academic_period_id
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Target examination does not belong "
                    "to the selected academic period."
                ),
            )


        # Ensure the target examination belongs to the selected period.
        if (
            payload.academic_period_id is not None
            and examination.academic_period_id
            != payload.academic_period_id
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Target examination does not belong "
                    "to the selected academic period."
                ),
            )

    try:
        result = ask_academic_assistant(
            db=db,
            institution_id=institution_id,
            question=payload.question,
            academic_period_id=(
                payload.academic_period_id
                or resolved["academic_period_id"]
            ),
            class_id=payload.class_id or resolved["class_id"],
            subject_id=(
                payload.subject_id
                or resolved["subject_id"]
            ),
            student_id=(
                payload.student_id
                or resolved["student_id"]
            ),
            target_examination_id=target_examination_id,
        )

        return AcademicAssistantResponse(**result)

    except APIError:
        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable. Please try again.",
        )

    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="The AI assistant is not configured correctly.",
        )
