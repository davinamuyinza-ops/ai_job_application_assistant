from fastapi import FastAPI
from pydantic import BaseModel
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

def request_ai (job_description: str, user_profile: str):
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
            "dynamic_entries": {}
            }

            Rules:

            - Extract information directly from the job description.
            - Do not invent information that is missing.
            - If information is missing, use empty strings or empty arrays.
            - ATS keywords should contain important searchable recruiter keywords.
            - recommendation should briefly explain whether the candidate is a strong fit.
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
            """
            },
            {
                "role": "user",
                "content": f"Description: {job_description}\nProfile: {user_profile}"
            }
        ]
    )

    return json.loads(response.output_text)

@app.post("/analyse-job")
def analyse_job(payload: JobRequest):
    ai_result= request_ai(payload.job_description, payload.user_profile)
    return ai_result


@app.get("/health")
def health():
    return {"status" : "ok"}