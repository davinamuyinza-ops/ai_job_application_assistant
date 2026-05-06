from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Job Application Assistant")

class JobRequest(BaseModel):
    job_description: str
    user_profile: str

@app.post("/analyse-job")
def analyse_job(payload: JobRequest):
    return {
        "received": True,
        "job_description": payload.job_description,
        "user_profile": payload.user_profile
    }


@app.get("/health")
def health():
    return {"status" : "ok"}