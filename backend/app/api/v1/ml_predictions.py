
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User
from app.ml.feature_service import build_prediction_features
from app.ml.prediction_service import predict_underperformance
from app.schemas.ml_predictions import (
    UnderperformancePredictionRequest,
    UnderperformancePredictionResponse,
)


router = APIRouter(
    prefix="/ml",
    tags=["ML Predictions"],
)


@router.post(
    "/predictions/underperformance",
    response_model=UnderperformancePredictionResponse,
    status_code=status.HTTP_200_OK,
)
def predict_student_underperformance(
    request: UnderperformancePredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    try:
        # Build features using only this institution's records.
        features = build_prediction_features(
            db=db,
            institution_id=institution_id,
            student_id=request.student_id,
            subject_id=request.subject_id,
            target_examination_id=request.target_examination_id,
        )

        # Run the trained Random Forest model.
        prediction = predict_underperformance(features)

        return {
            "student_id": request.student_id,
            "subject_id": request.subject_id,
            "target_examination_id": request.target_examination_id,
            **prediction,
            "features": features,
        }

    except ValueError as exc:
        message = str(exc)

        if "not found" in message.lower():
            error_status = status.HTTP_404_NOT_FOUND
        elif "marks already exist" in message.lower():
            error_status = status.HTTP_409_CONFLICT
        else:
            error_status = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=error_status,
            detail=message,
        )
