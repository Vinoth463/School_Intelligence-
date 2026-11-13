import sys
from pathlib import Path
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app
from app.api.dependencies import get_db, get_current_user
from app.database.connection import SessionLocal
from app.models import User
from app.models.examination import Examination
from app.models.marks import Mark
from app.models.student import Student
from app.models.academic_period import AcademicPeriod
from app.ml.feature_service import build_prediction_features
from app.ml.prediction_service import predict_underperformance

@pytest.fixture
def db_session():
    """Provide a database session and roll back test changes."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def test_user(db_session):
    """Load the existing admin test user."""
    user = db_session.query(User).filter(User.id == 1).first()

    assert user is not None, "Test user with ID 1 was not found."

    return user


@pytest.fixture
def target_examination(db_session, test_user):
    """Create a temporary future examination."""
    target_date = date(2026, 12, 15)

    exam = Examination(
        institution_id=test_user.institution_id,
        academic_period_id=2,
        name="Pytest Temporary ML Examination",
        exam_date=target_date,
        start_date=target_date,
        end_date=target_date,
        description="Temporary examination for automated ML tests.",
    )

    db_session.add(exam)
    db_session.flush()

    return exam


def test_ml_feature_generation(
    db_session,
    test_user,
    target_examination,
):
    """Verify database features are generated correctly."""

    features = build_prediction_features(
        db=db_session,
        institution_id=test_user.institution_id,
        student_id=1,
        subject_id=1,
        target_examination_id=target_examination.id,
    )

    assert isinstance(features, dict)

    expected_features = {
        "previous_exam_percentage",
        "historical_average_percentage",
        "marks_trend",
        "previous_exam_count",
        "attendance_percentage",
        "attendance_recent_60d",
        "attendance_previous_60d",
        "attendance_trend",
        "attendance_sessions_to_date",
        "class_grade",
    }

    assert expected_features.issubset(features.keys())

    assert features["previous_exam_count"] > 0
    assert features["class_grade"]


def test_ml_prediction_service(
    db_session,
    test_user,
    target_examination,
):
    """Verify the Random Forest prediction service."""

    features = build_prediction_features(
        db=db_session,
        institution_id=test_user.institution_id,
        student_id=1,
        subject_id=1,
        target_examination_id=target_examination.id,
    )

    result = predict_underperformance(features)

    assert isinstance(result, dict)
    assert isinstance(result["predicted_underperformance"], bool)

    assert result["risk_category"] in {
        "low",
        "medium",
        "high",
    }

    assert isinstance(result["risk_indicators"], list)
    assert isinstance(result["positive_indicators"], list)


def test_ml_prediction_api(
    db_session,
    test_user,
    target_examination,
):
    """Verify the actual authenticated ML prediction endpoint."""

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    payload = {
        "student_id": 1,
        "subject_id": 1,
        "target_examination_id": target_examination.id,
    }

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ml/predictions/underperformance",
                json=payload,
            )

        assert response.status_code == 200

        data = response.json()

        assert data["student_id"] == 1
        assert data["subject_id"] == 1
        assert data["target_examination_id"] == target_examination.id

        assert data["risk_category"] in {
            "low",
            "medium",
            "high",
        }

        assert "risk_indicators" in data
        assert "positive_indicators" in data
        assert "data_sufficiency_status" in data
        assert "data_sufficiency_warnings" in data

    finally:
        app.dependency_overrides.clear()


def test_ml_api_rejects_invalid_student(
    db_session,
    test_user,
    target_examination,
):
    """A non-existent student should return HTTP 404."""

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ml/predictions/underperformance",
                json={
                    "student_id": 999999,
                    "subject_id": 1,
                    "target_examination_id": target_examination.id,
                },
            )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()


def test_ml_api_rejects_invalid_subject(
    db_session,
    test_user,
    target_examination,
):
    """A non-existent subject should return HTTP 404."""

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ml/predictions/underperformance",
                json={
                    "student_id": 1,
                    "subject_id": 999999,
                    "target_examination_id": target_examination.id,
                },
            )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()


def test_ml_api_rejects_invalid_examination(
    db_session,
    test_user,
    target_examination,
):
    """A non-existent examination should return HTTP 404."""

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ml/predictions/underperformance",
                json={
                    "student_id": 1,
                    "subject_id": 1,
                    "target_examination_id": 999999,
                },
            )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()



def test_ml_api_rejects_existing_target_marks(
    db_session,
    test_user,
    target_examination,
):
    """Prediction must be rejected when target marks already exist."""

    # Retrieve the student's actual class.
    student = db_session.query(Student).filter(
        Student.id == 1,
        Student.institution_id == test_user.institution_id,
    ).first()

    assert student is not None

    # Insert a temporary mark for the target examination.
    temporary_mark = Mark(
        student_id=student.id,
        examination_id=target_examination.id,
        subject_id=1,
        class_id=student.class_id,
        obtained_marks=75,
        max_marks=100,
    )

    db_session.add(temporary_mark)
    db_session.flush()

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ml/predictions/underperformance",
                json={
                    "student_id": student.id,
                    "subject_id": 1,
                    "target_examination_id": target_examination.id,
                },
            )

        assert response.status_code == 409

        assert response.json()["detail"] == (
            "Marks already exist for the target examination."
        )

    finally:
        app.dependency_overrides.clear()



def test_ml_api_rejects_insufficient_historical_marks(
    db_session,
    test_user,
    target_examination,
):
    """Prediction must be rejected when no historical marks exist."""

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ml/predictions/underperformance",
                json={
                    "student_id": 201,
                    "subject_id": 3,
                    "target_examination_id": target_examination.id,
                },
            )

        assert response.status_code == 400

        assert response.json()["detail"] == (
            "Insufficient historical examination marks."
        )

    finally:
        app.dependency_overrides.clear()


def test_ml_api_blocks_student_from_another_institution(
    db_session,
    target_examination,
):
    """An institution must not access another institution's student."""

    # Simulate an authenticated user from a different institution.
    foreign_institution_user = SimpleNamespace(
        id=999,
        institution_id=999999,
    )

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return foreign_institution_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ml/predictions/underperformance",
                json={
                    "student_id": 1,
                    "subject_id": 1,
                    "target_examination_id": target_examination.id,
                },
            )

        assert response.status_code == 404

        assert response.json()["detail"] == (
            "Student not found in this institution."
        )

    finally:
        app.dependency_overrides.clear()

def test_ml_feature_generation_rejects_past_target_examination(
    db_session,
    test_user,
    target_examination,
):
    """Past examinations must not be used as prediction targets."""

    past_date = date.today() - timedelta(days=1)

    target_examination.exam_date = past_date
    target_examination.start_date = past_date
    target_examination.end_date = past_date

    db_session.flush()

    with pytest.raises(
        ValueError,
        match="Target examination must be in the future.",
    ):
        build_prediction_features(
            db=db_session,
            institution_id=test_user.institution_id,
            student_id=1,
            subject_id=1,
            target_examination_id=target_examination.id,
        )

def test_ml_feature_generation_rejects_exam_outside_academic_period(
    db_session,
    test_user,
    target_examination,
):
    """Reject an examination dated outside its academic period."""

    academic_period = db_session.get(
        AcademicPeriod,
        target_examination.academic_period_id,
    )

    outside_date = academic_period.end_date + timedelta(days=1)

    target_examination.exam_date = outside_date
    target_examination.start_date = outside_date
    target_examination.end_date = outside_date

    db_session.flush()

    with pytest.raises(
        ValueError,
        match="Target examination date is outside its academic period.",
    ):
        build_prediction_features(
            db=db_session,
            institution_id=test_user.institution_id,
            student_id=1,
            subject_id=1,
            target_examination_id=target_examination.id,
        )