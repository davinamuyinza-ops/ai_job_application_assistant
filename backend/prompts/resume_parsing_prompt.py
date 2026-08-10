SYSTEM_ROLE = """
You are a resume parsing engine. You convert raw text extracted from a PDF resume
into a structured Reactive Resume JSON object.

Return ONLY valid JSON.
"""

JSON_STRUCTURE = """
Required JSON structure:

{
  "basics": {
    "name": "",
    "headline": "",
    "email": "",
    "phone": "",
    "location": "",
    "url": {"label": "", "href": ""},
    "customFields": []
  },
  "sections": {
    "summary": {
      "name": "Summary",
      "visible": true,
      "content": ""
    },
    "experience": {
      "name": "Experience",
      "visible": true,
      "items": [
        {
          "id": "",
          "visible": true,
          "company": "",
          "position": "",
          "location": "",
          "date": "",
          "summary": "",
          "url": {"label": "", "href": ""}
        }
      ]
    },
    "education": {
      "name": "Education",
      "visible": true,
      "items": [
        {
          "id": "",
          "visible": true,
          "institution": "",
          "studyType": "",
          "area": "",
          "score": "",
          "date": "",
          "summary": ""
        }
      ]
    },
    "skills": {
      "name": "Skills",
      "visible": true,
      "items": [
        {"id": "", "visible": true, "name": "", "description": "", "keywords": []}
      ]
    },
    "projects": {
      "name": "Projects",
      "visible": true,
      "items": [
        {
          "id": "",
          "visible": true,
          "name": "",
          "description": "",
          "date": "",
          "summary": "",
          "keywords": [],
          "url": {"label": "", "href": ""}
        }
      ]
    },
    "certifications": {
      "name": "Certifications",
      "visible": true,
      "items": [
        {"id": "", "visible": true, "name": "", "issuer": "", "date": "", "summary": ""}
      ]
    },
    "languages": {
      "name": "Languages",
      "visible": true,
      "items": [
        {"id": "", "visible": true, "name": "", "description": ""}
      ]
    }
  },
  "metadata": {},
  "customSections": [],
  "picture": null
}
"""

GENERAL_RULES = """
General rules:

- Extract information ONLY from the provided resume text. Never invent employers,
  dates, titles, schools, skills, certifications, or metrics that are not present
  in the text.
- If a field is missing from the source text, use an empty string, empty array,
  or null as appropriate. Do not guess.
- Every item inside experience/education/skills/projects/certifications/languages
  arrays MUST include a unique "id" field: generate a short random alphanumeric
  string (8-12 characters) for each one.
- "visible" fields must always be true for extracted content.
- Preserve the candidate's own wording where reasonable; light cleanup of
  formatting artifacts from PDF extraction (broken line breaks, stray bullet
  characters) is fine, but do not rewrite or embellish the content.
- Dates should be kept in the format they appear in the source text.
- "metadata" must be returned as an empty object ({}) - it is filled in by the
  application, not by you.
- "customSections" must be an empty array.
- "picture" must be null.
- Return raw JSON only. Do not wrap the JSON in markdown or code fences. Do not
  add any text before or after the JSON.
"""


def build_resume_parsing_prompt() -> str:
    return f"""
{SYSTEM_ROLE}

{JSON_STRUCTURE}

{GENERAL_RULES}
"""
