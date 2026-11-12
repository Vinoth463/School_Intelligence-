
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.analytics_service import get_dashboard_overview


router = APIRouter(
    prefix="/dashboard",
    tags=["Academic Dashboard"],
)


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
)
def dashboard_overview(
    academic_period_id: int | None = Query(
        default=None,
        ge=1,
        description="Optional academic period filter",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return academic dashboard KPIs for the
    authenticated user's institution.
    """

    return get_dashboard_overview(
        db=db,
        institution_id=current_user.institution_id,
        academic_period_id=academic_period_id,
    )
