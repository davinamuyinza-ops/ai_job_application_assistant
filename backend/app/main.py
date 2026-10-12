from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import analysis, applications, jobs, resume, transcribe

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Job Application Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router)
app.include_router(analysis.router)
app.include_router(applications.router)
app.include_router(jobs.router)
app.include_router(transcribe.router)


@app.get("/health")
def health():
    return {"status": "ok"}
