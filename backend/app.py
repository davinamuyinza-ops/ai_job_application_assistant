from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from prompts.analysis_prompt import build_analysis_prompt
from prompts.resume_tailoring_prompt import build_resume_tailoring_prompt
from prompts.cover_letter_prompt import build_cover_letter_generation_prompt
from prompts.job_search_prompt import build_job_search_prompt
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="AI Job Application Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://ai-job-application-assist.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///applications.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()

class SavedApplication(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String)
    role = Column(String)
    match_score = Column(Integer)
    priority = Column(String)
    should_apply = Column(String)
    status = Column(String)
    application_date = Column(String)
    job_link = Column(String)

Base.metadata.create_all(bind=engine)

class SaveApplicationRequest(BaseModel):
    company: str
    role: str
    match_score: int
    priority: str
    should_apply: str
    status: str
    application_date: str
    job_link: str


class JobRequest(BaseModel):
    job_description: str
    resume_json: dict

class CoreFields(BaseModel):
    job_title: str
    company: str
    location: str
    employment_type: str
    experience_level: str
    salary: str
    remote_policy: str
    required_skills: list[str]
    preferred_skills: list[str]
    technologies: list[str]
    languages: list[str]
    responsibilities: list[str]
    benefits: list[str]
    ats_keywords: list[str]
    summary: str
    recommendation: str

class MatchAnalysis(BaseModel):
    match_score: int
    strong_matches: list[str]
    partial_matches: list[str]
    missing_requirements: list[str]
    risk_factors: list[str]
    application_recommendation: str

class Decision(BaseModel):
    should_apply: bool
    priority: str
    confidence: int
    reason: str

class CVTailoringPlan(BaseModel):
    recommended_cv_title: str
    profile_focus: str
    skills_to_emphasize: list[str]
    projects_to_emphasize: list[str]
    experience_to_emphasize: list[str]
    keywords_to_include: list[str]
    sections_to_adjust: list[str]
    tailoring_strategy: str

class CoverLetterPlan(BaseModel):
    tone: str
    main_motivation: str
    strongest_selling_points: list[str]
    company_alignment_points: list[str]
    key_experiences_to_mention: list[str]
    key_skills_to_highlight: list[str]
    suggested_opening_focus: str
    suggested_closing_focus: str
    things_to_avoid: list[str]

class RiskGapAnalysis(BaseModel):
    major_gaps: list[str]
    minor_gaps: list[str]
    potential_red_flags: list[str]
    compensation_strategies: list[str]
    interview_preparation_topics: list[str]
    estimated_competitiveness: str
    overall_risk_level: str

class WorkflowRecommendations(BaseModel):
    next_actions: list[str]
    documents_needed: list[str]
    application_priority_order: list[str]
    suggested_preparation_steps: list[str]
    follow_up_strategy: str
    estimated_application_effort: str
    networking_suggestions: list[str]
    deadline_awareness: str

class JobAnalysisResponse(BaseModel):
    core_fields: CoreFields
    match_analysis: MatchAnalysis
    dynamic_entries: dict
    decision: Decision
    cv_tailoring_plan: CVTailoringPlan
    cover_letter_plan: CoverLetterPlan
    risk_gap_analysis: RiskGapAnalysis
    workflow_recommendations: WorkflowRecommendations



class ResumeTailoringRequest(BaseModel):
    job_description: str
    resume_json: dict
    job_analysis: dict

class ResumeTailoringResponse(BaseModel):
    tailored_resume_json: dict
    change_summary: list[str]
    ats_keywords_added: list[str]
    sections_changed: list[str]


class CoverLetterGenerationRequest(BaseModel):
    job_description: str
    resume_json: dict
    job_analysis: dict

class CoverLetterGenerationResponse(BaseModel):
    cover_letter: str
    key_points_used: list[str]
    tone_used: str


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


def clean_ai_json(raw_text: str) -> str:
    text = raw_text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()

    if text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    return text

def run_full_job_analysis(job_description: str, user_profile: str):
    response = None
    ai_json = None
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": build_analysis_prompt()
                },
                {
                    "role": "user",
                    "content": f"Description: {job_description}\nProfile: {user_profile}"
                }
            ]
        )

        raw_output = response.output_text
        cleaned_output = clean_ai_json(raw_output)
        ai_json = json.loads(cleaned_output)
        validated_result = JobAnalysisResponse.model_validate(ai_json)
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
                "error": "AI response failed validation",
                "message": exc.errors(),
                "parsed_json": ai_json
            }
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected backend error",
                "message": str(error)
            }
        )

def tailor_resume_json(job_description: str, resume_json: dict, job_analysis: dict):
    response = None
    tailored_json = None

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": build_resume_tailoring_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
                        Job Description:
                        {job_description}

                        Deep Job Analysis:
                        {json.dumps(job_analysis)}

                        Reactive Resume JSON:
                        {json.dumps(resume_json)}
                    """
                }
            ]
        )

        raw_output = response.output_text

        cleaned_output = clean_ai_json(raw_output)

        tailored_json = json.loads(cleaned_output)

        validated_result = ResumeTailoringResponse.model_validate(tailored_json)
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

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected backend error",
                "message": str(error)
            }
        )

def generate_cover_letter(job_description: str, resume_json: dict, job_analysis: dict):
    response = None
    cover_letter_json = None

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": build_cover_letter_generation_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
                        Job Description:
                        {job_description}

                        Resume JSON:
                        {json.dumps(resume_json)}

                        Deep Job Analysis:
                        {json.dumps(job_analysis)}

                        Return ONLY valid JSON with this structure:
                        {{
                        "cover_letter": "",
                        "key_points_used": [],
                        "tone_used": ""
                        }}
                    """
                }
            ]
        )

        raw_output = response.output_text
        cleaned_output = clean_ai_json(raw_output)
        cover_letter_json = json.loads(cleaned_output)

        validated_result = CoverLetterGenerationResponse.model_validate(cover_letter_json)
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
                "error": "AI response failed validation",
                "message": exc.errors(),
                "parsed_json": cover_letter_json
            }
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected backend error",
                "message": str(error)
            }
        )

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
            input=[
                {
                    "role": "system",
                    "content": build_job_search_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
                    Resume JSON:
                    {json.dumps(resume_json)}
                    """
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
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
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


@app.post("/analyze-job")
def analyze_job(payload: JobRequest):
    resume_profile = json.dumps(payload.resume_json)

    ai_result = run_full_job_analysis(
        payload.job_description,
        resume_profile
    )
    return ai_result

@app.post("/tailor-resume")
def tailor_resume(payload: ResumeTailoringRequest):
    result = tailor_resume_json(
        payload.job_description,
        payload.resume_json,
        payload.job_analysis
    )
    return result

@app.post("/generate-cover-letter")
def cover_letter(payload: CoverLetterGenerationRequest):
    result = generate_cover_letter(
        payload.job_description,
        payload.resume_json,
        payload.job_analysis
    )
    return result

@app.post("/extract-job")
def extract_job(payload: JobUrlRequest):
    job_text = extract_job_text_from_url(payload.job_url)

    return JobUrlResponse(job_text=job_text)

@app.post("/search-jobs")
def search_jobs(payload: JobSearchRequest):

    strategy = generate_search_queries(
        payload.resume_json
    )

    all_jobs = []

    for query in strategy.search_queries[:3]:

        try:
            results = search_serper(query)

            extracted_jobs = extract_jobs_from_results(
                results
            )

            all_jobs.extend(extracted_jobs)

        except Exception as exc:
            print(f"Search failed for query: {query}")
            print(exc)

    return JobSearchResponse(
        jobs=all_jobs
    )

@app.post("/generate-search-queries")
def generate_queries(payload: SearchQueryRequest):
    result = generate_search_queries(payload.resume_json)
    return result

@app.post("/save-application")
def save_application(payload: SaveApplicationRequest):

    db = SessionLocal()

    saved_application = SavedApplication(
        company=payload.company,
        role=payload.role,
        match_score=payload.match_score,
        priority=payload.priority,
        should_apply=payload.should_apply,
        status=payload.status,
        application_date=payload.application_date,
        job_link=payload.job_link
    )

    db.add(saved_application)
    db.commit()
    db.refresh(saved_application)
    db.close()

    return {
        "message": "Application saved successfully",
        "id": saved_application.id
    }

@app.get("/applications")
def get_applications():

    db = SessionLocal()

    applications = db.query(SavedApplication).all()

    db.close()

    return applications

@app.delete("/applications/{application_id}")
def delete_application(application_id: int):

    db = SessionLocal()

    application = db.query(SavedApplication).filter(
        SavedApplication.id == application_id
    ).first()

    if application:

        db.delete(application)
        db.commit()

    db.close()

    return {
        "message": "Application deleted"
    }

@app.put("/applications/{application_id}/status")
def update_application_status_backend(application_id: int, status: str):

    db = SessionLocal()

    application = db.query(SavedApplication).filter(
        SavedApplication.id == application_id
    ).first()

    if application:
        application.status = status
        db.commit()

    db.close()

    return {
        "message": "Status updated"
    }

@app.get("/health")
def health():
    return {"status" : "ok"}