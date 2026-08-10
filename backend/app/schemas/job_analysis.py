from pydantic import BaseModel


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
