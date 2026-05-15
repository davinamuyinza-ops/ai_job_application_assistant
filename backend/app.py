from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from prompts.analysis_prompt import build_analysis_prompt
from prompts.resume_tailoring_prompt import build_resume_tailoring_prompt
from prompts.cover_letter_prompt import build_cover_letter_generation_prompt
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="AI Job Application Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    jobs = [
        {
            "title": "Working Student AI Automation",
            "company": "Example AI Company",
            "location": "Remote",
            "reason": "Matches AI workflow, JavaScript, Python, and automation experience.",
            "link": "https://example.com/job1"
        },
        {
            "title": "Werkstudent Software Testing",
            "company": "Example Tech GmbH",
            "location": "Düsseldorf",
            "reason": "Matches QA, debugging, testing, and structured documentation experience.",
            "link": "https://example.com/job2"
        }
    ]

    return JobSearchResponse(jobs=jobs)

@app.get("/health")
def health():
    return {"status" : "ok"}