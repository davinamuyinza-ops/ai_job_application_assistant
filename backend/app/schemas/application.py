from pydantic import BaseModel


class SaveApplicationRequest(BaseModel):
    company: str
    role: str
    match_score: int
    priority: str
    should_apply: str
    status: str
    application_date: str
    job_link: str
    job_analysis: dict
    tailored_resume: dict | None = None
    cover_letter: str | None = None
    job_description: str | None = None


class ApplicationResponse(BaseModel):
    id: int
    company: str
    role: str
    match_score: int
    priority: str
    should_apply: str
    status: str
    application_date: str
    job_link: str
    job_analysis: dict | None
    # The documents themselves are fetched on demand; the list only says
    # whether they exist so it stays small.
    has_tailored_resume: bool = False
    has_cover_letter: bool = False

    model_config = {"from_attributes": True}


class ApplicationDocuments(BaseModel):
    tailored_resume: dict | None = None
    cover_letter: str | None = None
    job_description: str | None = None
