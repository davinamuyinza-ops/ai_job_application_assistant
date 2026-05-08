from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

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


SYSTEM_ROLE = """
You are an advanced AI recruitment, ATS, and career analysis assistant.

Analyze the provided job description carefully and extract all important information that would help a candidate:
- understand the role
- decide whether to apply
- tailor a CV
- tailor a cover letter
- optimize for ATS systems

Return ONLY valid JSON.
"""

JSON_STRUCTURE = """
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
  },
  "cv_tailoring_plan": {
    "recommended_cv_title": "",
    "profile_focus": "",
    "skills_to_emphasize": [],
    "projects_to_emphasize": [],
    "experience_to_emphasize": [],
    "keywords_to_include": [],
    "sections_to_adjust": [],
    "tailoring_strategy": ""
  },
  "cover_letter_plan": {
    "tone": "",
    "main_motivation": "",
    "strongest_selling_points": [],
    "company_alignment_points": [],
    "key_experiences_to_mention": [],
    "key_skills_to_highlight": [],
    "suggested_opening_focus": "",
    "suggested_closing_focus": "",
    "things_to_avoid": []
  },
  "risk_gap_analysis": {
    "major_gaps": [],
    "minor_gaps": [],
    "potential_red_flags": [],
    "compensation_strategies": [],
    "interview_preparation_topics": [],
    "estimated_competitiveness": "",
    "overall_risk_level": ""
  },
  "workflow_recommendations": {
    "next_actions": [],
    "documents_needed": [],
    "application_priority_order": [],
    "suggested_preparation_steps": [],
    "follow_up_strategy": "",
    "estimated_application_effort": "",
    "networking_suggestions": [],
    "deadline_awareness": ""
  }
}
"""

GENERAL_RULES = """
General rules:

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
- Use clear concise values.
- Return raw JSON only.
- Do not wrap the JSON in markdown.
- Do not use ```json.
- Do not use code fences.
- Return no text before or after the JSON.
"""

CV_RULES = """
CV tailoring rules:

- Emphasize strongest matching skills.
- Optimize for ATS keywords.
- Prioritize relevant projects.
- Reduce unrelated focus.
- Align CV title with the role.
"""

COVER_LETTER_RULES = """
Cover letter planning rules:

- cover_letter_plan must not write the full cover letter.
- It must only plan what the cover letter should focus on.
- tone must match the job description language and company style.
- main_motivation must connect the candidate’s background with the role.
- strongest_selling_points must come from the user_profile.
- company_alignment_points must come from the job description.
- key_experiences_to_mention must select only relevant experience.
- key_skills_to_highlight must prioritize skills from the job requirements.
- suggested_opening_focus must explain what the first paragraph should emphasize.
- suggested_closing_focus must explain what the final paragraph should emphasize.
- things_to_avoid must list irrelevant or weak topics that should not be emphasized.
- Do not invent company facts that are not in the job description.
- Keep all values concise and application-focused.
"""

RISK_RULES = """
Risk and gap analysis rules:

- major_gaps must contain important missing requirements.
- minor_gaps must contain smaller missing skills or experiences.
- potential_red_flags must identify possible recruiter concerns.
- compensation_strategies must explain how the candidate can offset weaknesses.
- interview_preparation_topics must suggest areas the candidate should prepare for.
- estimated_competitiveness must estimate how competitive the candidate is for the role.
- overall_risk_level must be low, medium, or high.
- Do not invent unrealistic risks.
- Focus only on information present in the profile and job description.
"""

WORKFLOW_RULES = """
Workflow recommendation rules:

- next_actions must contain practical next steps for the candidate.
- documents_needed must identify required or useful documents.
- application_priority_order must explain what should be done first.
- suggested_preparation_steps must help improve application quality.
- follow_up_strategy must explain whether and how to follow up.
- estimated_application_effort must be low, medium, or high.
- networking_suggestions must suggest useful networking opportunities if relevant.
- deadline_awareness must mention urgency or important timing considerations.
- Recommendations must be practical and realistic.
- Avoid generic advice.
"""

def build_analysis_prompt() -> str:
    return f"""
{SYSTEM_ROLE}

{JSON_STRUCTURE}

{GENERAL_RULES}

{CV_RULES}

{COVER_LETTER_RULES}

{RISK_RULES}

{WORKFLOW_RULES}
"""

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

@app.post("/analyze-job")
def analyze_job(payload: JobRequest):
    ai_result= run_full_job_analysis(payload.job_description, payload.user_profile)
    return ai_result


@app.get("/health")
def health():
    return {"status" : "ok"}