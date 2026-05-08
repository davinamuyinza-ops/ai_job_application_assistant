from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="AI Job Application Assistant")

class JobRequest(BaseModel):
    job_description: str
    user_profile: str

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


class JobAnalysisResponse(BaseModel):
    core_fields: CoreFields
    match_analysis: MatchAnalysis
    dynamic_entries: dict
    decision: Decision

def clean_ai_json(raw_text: str) -> str:
    text = raw_text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()

    if text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    return text

def request_ai (job_description: str, user_profile: str):
    response = None
    ai_json = None
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": """
                You are an advanced AI recruitment, ATS, and career analysis assistant.

                Analyze the provided job description carefully and extract all important information that would help a candidate:
                - understand the role
                - decide whether to apply
                - tailor a CV
                - tailor a cover letter
                - optimize for ATS systems

                Return ONLY valid JSON.

                Required JSON structure:

                {
                "core_fields": {
                    "job_title": "",
                    "company": "",
                    "location": "",
                    "employment_type": "",
                    "experience_level": "",
                    "salary": "",
                    "remote_policy": "",
                    "required_skills": [],
                    "preferred_skills": [],
                    "technologies": [],
                    "languages": [],
                    "responsibilities": [],
                    "benefits": [],
                    "ats_keywords": [],
                    "summary": "",
                    "recommendation": ""
                },
                "match_analysis": {
                    "match_score": 0,
                    "strong_matches": [],
                    "partial_matches": [],
                    "missing_requirements": [],
                    "risk_factors": [],
                    "application_recommendation": ""
                },
                "dynamic_entries": {},
                "decision": {
                    "should_apply": true,
                    "priority": "high",
                    "confidence": 85,
                    "reason": ""
                }
                }

                Rules:

                - Extract information directly from the job description.
                - Do not invent information that is missing.
                - If information is missing, use empty strings or empty arrays.
                - ATS keywords should contain important searchable recruiter keywords.
                - recommendation should briefly explain whether the candidate is a strong fit.
                - match_score must be an integer from 0 to 100.
                - should_apply must be true only if the candidate is a reasonable fit.
                - should_apply must be false if the role has major missing requirements, wrong location, wrong language, wrong experience level, or does not match the candidate profile.
                - priority must be one of: high, medium, low.
                - confidence must be an integer from 0 to 100.
                - confidence means how sure you are about your decision.
                - reason must explain the decision briefly.
                - dynamic_entries must contain additional useful information discovered in the job description.
                - dynamic_entries may create new keys dynamically depending on the content of the job description.
                - Examples of possible dynamic_entries:
                - visa_sponsorship
                - travel_requirement
                - security_clearance
                - relocation_support
                - shift_work
                - probation_period
                - student_status_required
                - driver's_license_required
                - certifications
                - industry
                - team_structure
                - contract_duration
                - Use clear concise values.
                - Return no text outside JSON.
                - Return raw JSON only.
                - Do not wrap the JSON in markdown.
                - Do not use ```json.
                - Do not use code fences.
                - Return no text before or after the JSON.
                """
                },
                {
                    "role": "user",
                    "content": f"Description: {job_description}\nProfile: {user_profile}"
                }
            ]
        )

        raw_output = response.output_text
        print("RAW AI RESPONSE:", raw_output)
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

@app.post("/analyze-job")
def analyze_job(payload: JobRequest):
    ai_result= request_ai(payload.job_description, payload.user_profile)
    return ai_result


@app.get("/health")
def health():
    return {"status" : "ok"}