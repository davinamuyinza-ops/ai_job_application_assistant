from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.models.application import Application
from app.schemas.application import ApplicationResponse, SaveApplicationRequest

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/save-application")
def save_application(
    payload: SaveApplicationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved_application = Application(
        user_id=current_user.id,
        company=payload.company,
        role=payload.role,
        match_score=payload.match_score,
        priority=payload.priority,
        should_apply=payload.should_apply,
        status=payload.status,
        application_date=payload.application_date,
        job_link=payload.job_link,
        job_analysis=payload.job_analysis,
    )

    db.add(saved_application)
    db.commit()
    db.refresh(saved_application)

    return {
        "message": "Application saved successfully",
        "id": saved_application.id,
    }


@router.get("/applications", response_model=list[ApplicationResponse])
def get_applications(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Application)
        .filter(Application.user_id == current_user.id)
        .all()
    )


@router.delete("/applications/{application_id}")
def delete_application(
    application_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )

    if application:
        db.delete(application)
        db.commit()

    return {"message": "Application deleted"}


@router.put("/applications/{application_id}/status")
def update_application_status(
    application_id: int,
    status: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )

    if application:
        application.status = status
        db.commit()

    return {"message": "Status updated"}
