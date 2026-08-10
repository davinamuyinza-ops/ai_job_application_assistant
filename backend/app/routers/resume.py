from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.models.master_resume import MasterResume
from app.schemas.resume import (
    MasterResumeResponse,
    MasterResumeUpsertRequest,
    ResumeParsePdfResponse,
)
from app.services.pdf_extraction import parse_resume_pdf_to_json

router = APIRouter(tags=["master-resume"])


@router.get("/master-resume", response_model=MasterResumeResponse)
def get_master_resume(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(MasterResume)
        .filter(MasterResume.user_id == current_user.id)
        .first()
    )

    if not resume:
        raise HTTPException(status_code=404, detail="No master resume saved yet")

    return resume


@router.put("/master-resume", response_model=MasterResumeResponse)
def upsert_master_resume(
    payload: MasterResumeUpsertRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(MasterResume)
        .filter(MasterResume.user_id == current_user.id)
        .first()
    )

    if resume:
        resume.resume_json = payload.resume_json
        resume.source_type = payload.source_type
    else:
        resume = MasterResume(
            user_id=current_user.id,
            resume_json=payload.resume_json,
            source_type=payload.source_type,
        )
        db.add(resume)

    db.commit()
    db.refresh(resume)

    return resume


@router.post("/master-resume/parse-pdf", response_model=ResumeParsePdfResponse)
async def parse_master_resume_pdf(
    file: UploadFile,
    current_user: CurrentUser = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    file_bytes = await file.read()

    resume_json = parse_resume_pdf_to_json(file_bytes)

    return ResumeParsePdfResponse(resume_json=resume_json)
