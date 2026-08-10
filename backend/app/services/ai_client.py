from openai import OpenAI

from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)


def clean_ai_json(raw_text: str) -> str:
    text = raw_text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()

    if text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    return text


def build_language_lock(target_language: str, document_type: str) -> str:
    return f"""
    ABSOLUTE LANGUAGE ENFORCEMENT:

    TARGET_LANGUAGE = {target_language}

    The final {document_type} MUST be written completely in {target_language}.

    The language of:
    - resume_json
    - job_analysis
    - original resume
    - previous outputs

    is NOT authoritative.

    Only the job description language is authoritative.

    IMPORTANT:

    The job_analysis may contain English even when the target language is German.
    Ignore the language of the job_analysis.
    Use only its meaning and factual information.

    The resume_json may contain English.
    Ignore its language.
    Use only its factual information.

    You MUST rewrite all visible recruiter-facing content into {target_language}.

    This includes:
    - summaries
    - headlines
    - section titles
    - descriptions
    - bullet points
    - project descriptions
    - education descriptions
    - skills categories
    - recommendations
    - explanations

    Keep JSON keys unchanged.
    Translate JSON values only.

    If TARGET_LANGUAGE is German:
    - all recruiter-facing text must be German
    - do not leave English bullet points
    - do not leave English summaries
    - do not leave English section titles

    If TARGET_LANGUAGE is English:
    - all recruiter-facing text must be English
    - do not leave German bullet points
    - do not leave German summaries
    - do not leave German section titles

    Allowed unchanged technical terms:
    - Python
    - JavaScript
    - React
    - FastAPI
    - REST API
    - Git
    - GitHub
    - SQL
    - HTML
    - CSS
    - Jira

    Mixed-language output is invalid.

    Before returning the JSON:
    check every visible value and rewrite it into {target_language}.

    Return only valid JSON.
    """
