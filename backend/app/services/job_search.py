import json

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.job_search import SearchQueryResponse
from app.services.ai_client import client, clean_ai_json
from prompts.job_match_prompt import build_job_match_prompt
from prompts.job_search_prompt import build_job_search_prompt


def extract_job_text_from_url(job_url: str):
    try:
        response = requests.get(job_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        cleaned_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        job_text = "\n".join(cleaned_lines)

        return job_text[:8000]

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Could not extract job text from URL",
                "message": str(error)
            }
        )


def generate_search_queries(resume_json: dict):
    response = None
    search_json = None

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0,
            input=[
                {
                    "role": "system",
                    "content": build_job_search_prompt()
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "resume_json": resume_json
                        },
                        ensure_ascii=False
                    )
                }
            ]
        )

        raw_output = response.output_text
        cleaned_output = clean_ai_json(raw_output)
        search_json = json.loads(cleaned_output)

        validated_result = SearchQueryResponse.model_validate(search_json)
        return validated_result

    except json.JSONDecodeError as exc:
        raw_output = response.output_text if response else "No response received"

        raise HTTPException(
            status_code=500,
            detail={
                "error": "AI returned invalid JSON",
                "message": str(exc),
                "raw_response": raw_output
            }
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Search query response failed validation",
                "message": exc.errors(),
                "parsed_json": search_json
            }
        )


def search_adzuna(
    query: str,
    location: str,
    country: str,
    page: int = 1,
    job_types: list[str] | None = None,
    salary_min: int | None = None,
    salary_max: int | None = None,
    max_days_old: int | None = None,
    distance: int | None = None,
):
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "what": query,
        "where": location,
        "results_per_page": 20,
        "content-type": "application/json"
    }

    for job_type in job_types or []:
        params[job_type] = 1

    if salary_min is not None:
        params["salary_min"] = salary_min

    if salary_max is not None:
        params["salary_max"] = salary_max

    if max_days_old is not None:
        params["max_days_old"] = max_days_old

    if distance is not None:
        params["distance"] = distance

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def extract_jobs_from_adzuna(results: dict):
    jobs = []

    for item in results.get("results", []):
        jobs.append(
            {
                "title": item.get("title", "Unknown Job"),
                "company": (item.get("company") or {}).get("display_name", "Unknown Company"),
                "location": (item.get("location") or {}).get("display_name", "Unknown Location"),
                "description": item.get("description", ""),
                "link": item.get("redirect_url", "")
            }
        )

    return jobs


def score_job_matches(resume_json: dict, jobs: list[dict]):
    if not jobs:
        return []

    response = None
    scores_json = None

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0,
            input=[
                {
                    "role": "system",
                    "content": build_job_match_prompt()
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "resume_json": resume_json,
                            "jobs": [
                                {
                                    "link": job["link"],
                                    "title": job["title"],
                                    "company": job["company"],
                                    "location": job["location"],
                                    "description": job["description"][:500]
                                }
                                for job in jobs
                            ]
                        },
                        ensure_ascii=False
                    )
                }
            ]
        )

        raw_output = response.output_text
        cleaned_output = clean_ai_json(raw_output)
        scores_json = json.loads(cleaned_output)

        scores_by_link = {
            entry["link"]: entry
            for entry in scores_json
            if isinstance(entry, dict) and "link" in entry
        }

        scored_jobs = []
        for job in jobs:
            score_entry = scores_by_link.get(job["link"])
            if not score_entry:
                continue

            scored_jobs.append(
                {
                    "title": job["title"],
                    "company": job["company"],
                    "location": job["location"],
                    "link": job["link"],
                    "match_score": score_entry.get("match_score", 0),
                    "reason": score_entry.get("reason", "")
                }
            )

        scored_jobs.sort(key=lambda job: job["match_score"], reverse=True)

        return scored_jobs[:15]

    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        raw_output = response.output_text if response else "No response received"

        raise HTTPException(
            status_code=500,
            detail={
                "error": "AI returned invalid job match scoring JSON",
                "message": str(exc),
                "raw_response": raw_output
            }
        )
