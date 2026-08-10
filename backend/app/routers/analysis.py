import json

from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.schemas.cover_letter import (
    CoverLetterGenerationRequest,
    CoverLetterGenerationResponse,
)
from app.schemas.job_analysis import JobAnalysisResponse, JobRequest
from app.schemas.job_search import JobUrlRequest, JobUrlResponse
from app.schemas.resume import ResumeTailoringRequest, ResumeTailoringResponse
from app.services.ai_analysis import run_full_job_analysis
from app.services.ai_cover_letter import generate_cover_letter
from app.services.ai_resume import tailor_resume_json
from app.services.job_search import extract_job_text_from_url

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/analyze-job", response_model=JobAnalysisResponse)
def analyze_job(payload: JobRequest):
    resume_profile = json.dumps(payload.resume_json, ensure_ascii=False)

    return run_full_job_analysis(
        payload.job_description,
        resume_profile,
    )


@router.post("/tailor-resume", response_model=ResumeTailoringResponse)
def tailor_resume(payload: ResumeTailoringRequest):
    return tailor_resume_json(
        payload.job_description,
        payload.resume_json,
        payload.job_analysis,
    )


@router.post("/generate-cover-letter", response_model=CoverLetterGenerationResponse)
def cover_letter(payload: CoverLetterGenerationRequest):
    return generate_cover_letter(
        payload.job_description,
        payload.resume_json,
        payload.job_analysis,
    )


@router.post("/extract-job", response_model=JobUrlResponse)
def extract_job(payload: JobUrlRequest):
    job_text = extract_job_text_from_url(payload.job_url)

    return JobUrlResponse(job_text=job_text)
