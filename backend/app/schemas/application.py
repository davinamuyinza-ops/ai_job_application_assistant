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
