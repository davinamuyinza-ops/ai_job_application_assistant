from pydantic import BaseModel


class CoverLetterGenerationRequest(BaseModel):
    job_description: str
    resume_json: dict
    job_analysis: dict
    personal_motivation: str | None = None


class CoverLetterGenerationResponse(BaseModel):
    cover_letter: str
    key_points_used: list[str]
    tone_used: str
