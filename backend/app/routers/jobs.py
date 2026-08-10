from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.job_search import (
    JobSearchRequest,
    JobSearchResponse,
    SearchQueryRequest,
    SearchQueryResponse,
)
from app.services.job_search import (
    extract_jobs_from_results,
    generate_search_queries,
    search_serper,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/search-jobs", response_model=JobSearchResponse)
def search_jobs(payload: JobSearchRequest):
    strategy = generate_search_queries(payload.resume_json)

    all_jobs = []

    for query in strategy.search_queries[:3]:
        try:
            results = search_serper(query)
            extracted_jobs = extract_jobs_from_results(results)
            all_jobs.extend(extracted_jobs)

        except Exception as exc:
            print(f"Search failed for query: {query}")
            print(exc)

    return JobSearchResponse(jobs=all_jobs)


@router.post("/generate-search-queries", response_model=SearchQueryResponse)
def generate_queries(payload: SearchQueryRequest):
    return generate_search_queries(payload.resume_json)
