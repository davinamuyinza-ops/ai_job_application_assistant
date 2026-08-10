from pydantic import BaseModel


class JobUrlRequest(BaseModel):
    job_url: str


class JobUrlResponse(BaseModel):
    job_text: str


class JobSearchRequest(BaseModel):
    resume_json: dict


class PromisingJob(BaseModel):
    title: str
    company: str
    location: str
    reason: str
    link: str


class JobSearchResponse(BaseModel):
    jobs: list[PromisingJob]


class SearchQueryRequest(BaseModel):
    resume_json: dict


class SearchQueryResponse(BaseModel):
    search_queries: list[str]
    target_roles: list[str]
    strongest_keywords: list[str]
    excluded_roles: list[str]
