from datetime import datetime

from pydantic import BaseModel


class ResumeTailoringRequest(BaseModel):
    job_description: str
    resume_json: dict
    job_analysis: dict


class ResumeTailoringResponse(BaseModel):
    tailored_resume_json: dict
    change_summary: list[str]
    ats_keywords_added: list[str]
    sections_changed: list[str]


class MasterResumeUpsertRequest(BaseModel):
    resume_json: dict
    source_type: str = "json_upload"


class MasterResumeResponse(BaseModel):
    id: int
    resume_json: dict
    source_type: str
    preferred_template: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeParsePdfResponse(BaseModel):
    resume_json: dict
