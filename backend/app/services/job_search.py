import json

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.job_search import SearchQueryResponse
from app.services.ai_client import client, clean_ai_json
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


def search_serper(query: str):
    url = "https://google.serper.dev/search"

    headers = {
        "X-API-KEY": settings.serper_api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "q": f'{query} "working student" OR "werkstudent" "apply" "job" (site:boards.greenhouse.io OR site:jobs.lever.co OR site:jobs.personio.de)',
        "num": 10
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def extract_jobs_from_results(results: dict):
    jobs = []

    organic_results = results.get("organic", [])

    blocked_domains = [
        "glassdoor",
        "indeed",
        "linkedin",
        "simplyhired",
        "jooble",
        "jobsora"
    ]

    blocked_title_words = [
        "careers",
        "open positions",
        "current job openings",
        "jobs at",
        "career opportunities"
    ]

    for item in organic_results:
        link = item.get("link", "")
        title = item.get("title", "")

        if any(word in title.lower() for word in blocked_title_words):
            continue

        if any(domain in link.lower() for domain in blocked_domains):
            continue

        jobs.append(
            {
                "title": item.get("title", "Unknown Job"),
                "company": "Unknown Company",
                "location": "Unknown Location",
                "reason": item.get("snippet", ""),
                "link": link
            }
        )

    return jobs
