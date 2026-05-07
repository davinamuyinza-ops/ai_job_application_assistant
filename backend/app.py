from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI

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
        input=f"""
        you are a job application assisatnt. 
        you extract everything i need to know about the job.
        return the details as a summary of the job description

        job:
        Description:{job_description} 
        Profile:{user_profile}
        """
    )

    return response.output_text

@app.post("/analyse-job")
def analyse_job(payload: JobRequest):
    ai_result= request_ai(payload.job_description, payload.user_profile)
    return {
        "job_summary": ai_result
        
    }


@app.get("/health")
def health():
    return {"status" : "ok"}