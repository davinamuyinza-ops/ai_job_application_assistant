from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.models.application import Application
from app.schemas.application import (
    ApplicationDocuments,
    ApplicationResponse,
    SaveApplicationRequest,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


def _find_own_application(db: Session, application_id: int, user_id: str) -> Application:
    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == user_id)
        .first()
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


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
        tailored_resume=payload.tailored_resume,
        cover_letter=payload.cover_letter,
        job_description=payload.job_description,
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
    applications = (
        db.query(Application)
        .filter(Application.user_id == current_user.id)
        .all()
    )

    return [
        ApplicationResponse.model_validate(application).model_copy(
            update={
                "has_tailored_resume": application.tailored_resume is not None,
                "has_cover_letter": bool(application.cover_letter),
            }
        )
        for application in applications
    ]


@router.get("/applications/{application_id}/documents", response_model=ApplicationDocuments)
def get_application_documents(
    application_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _find_own_application(db, application_id, current_user.id)


@router.put("/applications/{application_id}/documents")
def update_application_documents(
    application_id: int,
    payload: ApplicationDocuments,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = _find_own_application(db, application_id, current_user.id)

    # Only touch fields the caller actually sent, so saving an edited resume
    # doesn't wipe the stored cover letter (or vice versa).
    for field in payload.model_fields_set:
        setattr(application, field, getattr(payload, field))

    db.commit()

    return {"message": "Documents saved"}


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
