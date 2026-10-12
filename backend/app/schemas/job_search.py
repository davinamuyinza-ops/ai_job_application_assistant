from pydantic import BaseModel


class JobUrlRequest(BaseModel):
    job_url: str


class JobUrlResponse(BaseModel):
    job_text: str


class JobSearchRequest(BaseModel):
    resume_json: dict
    country: str = "de"
    location: str | None = None
    selected_sectors: list[str] | None = None
    job_types: list[str] | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    max_days_old: int | None = None
    distance: int | None = None


class PromisingJob(BaseModel):
    title: str
    company: str
    location: str
    reason: str
    link: str
    match_score: int


class JobSearchResponse(BaseModel):
    jobs: list[PromisingJob]


class SearchQueryRequest(BaseModel):
    resume_json: dict


class SearchQueryItem(BaseModel):
    query: str
    sector: str


class SearchQueryResponse(BaseModel):
    search_queries: list[SearchQueryItem]
    target_roles: list[str]
    strongest_keywords: list[str]
    excluded_roles: list[str]
    location: str
    sectors: list[str]
