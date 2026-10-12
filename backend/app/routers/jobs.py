from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.job_search import (
    JobSearchRequest,
    JobSearchResponse,
    SearchQueryRequest,
    SearchQueryResponse,
)
from app.services.job_search import (
    extract_jobs_from_adzuna,
    generate_search_queries,
    score_job_matches,
    search_adzuna,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/search-jobs", response_model=JobSearchResponse)
def search_jobs(payload: JobSearchRequest):
    strategy = generate_search_queries(payload.resume_json)

    location = payload.location or strategy.location

    queries = strategy.search_queries
    if payload.selected_sectors:
        filtered = [q for q in queries if q.sector in payload.selected_sectors]
        if filtered:
            queries = filtered

    all_jobs = []
    seen_links = set()

    for item in queries[:3]:
        try:
            results = search_adzuna(
                item.query,
                location,
                payload.country,
                job_types=payload.job_types,
                salary_min=payload.salary_min,
                salary_max=payload.salary_max,
                max_days_old=payload.max_days_old,
                distance=payload.distance,
            )
            extracted_jobs = extract_jobs_from_adzuna(results)

            for job in extracted_jobs:
                if job["link"] and job["link"] not in seen_links:
                    seen_links.add(job["link"])
                    all_jobs.append(job)

        except Exception as exc:
            print(f"Search failed for query: {item.query}")
            print(exc)

    scored_jobs = score_job_matches(payload.resume_json, all_jobs)

    return JobSearchResponse(jobs=scored_jobs)


@router.post("/generate-search-queries", response_model=SearchQueryResponse)
def generate_queries(payload: SearchQueryRequest):
    return generate_search_queries(payload.resume_json)
