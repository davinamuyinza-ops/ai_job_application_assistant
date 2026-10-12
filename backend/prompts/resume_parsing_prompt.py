SYSTEM_ROLE = """
You are a resume parsing engine. You convert raw text extracted from a PDF resume
into a structured Reactive Resume JSON object, matching the real Reactive Resume
data model exactly.

Return ONLY valid JSON.
"""

JSON_STRUCTURE = """
Required JSON structure:

{
  "picture": {
    "hidden": true,
    "url": "",
    "size": 90,
    "rotation": 0,
    "aspectRatio": 1,
    "borderRadius": 0,
    "borderColor": "rgba(0, 0, 0, 0)",
    "borderWidth": 0,
    "shadowColor": "rgba(0, 0, 0, 0.5)",
    "shadowWidth": 0
  },
  "basics": {
    "name": "",
    "headline": "",
    "email": "",
    "phone": "",
    "location": "",
    "website": {"url": "", "label": ""},
    "customFields": [
      {"id": "", "icon": "", "text": "", "link": ""}
    ]
  },
  "summary": {
    "title": "Summary",
    "hidden": false,
    "content": ""
  },
  "sections": {
    "experience": {
      "title": "Experience",
      "hidden": false,
      "items": [
        {
          "id": "",
          "hidden": false,
          "company": "",
          "position": "",
          "location": "",
          "period": "",
          "website": {"url": "", "label": ""},
          "description": ""
        }
      ]
    },
    "education": {
      "title": "Education",
      "hidden": false,
      "items": [
        {
          "id": "",
          "hidden": false,
          "school": "",
          "degree": "",
          "area": "",
          "grade": "",
          "location": "",
          "period": "",
          "website": {"url": "", "label": ""},
          "description": ""
        }
      ]
    },
    "projects": {
      "title": "Projects",
      "hidden": false,
      "items": [
        {
          "id": "",
          "hidden": false,
          "name": "",
          "period": "",
          "website": {"url": "", "label": ""},
          "description": ""
        }
      ]
    },
    "skills": {
      "title": "Skills",
      "hidden": false,
      "items": [
        {
          "id": "",
          "hidden": false,
          "name": "",
          "proficiency": "",
          "level": 0,
          "keywords": []
        }
      ]
    },
    "languages": {
      "title": "Languages",
      "hidden": false,
      "items": [
        {"id": "", "hidden": false, "language": "", "fluency": "", "level": 0}
      ]
    },
    "volunteer": {
      "title": "Volunteering",
      "hidden": false,
      "items": [
        {
          "id": "",
          "hidden": false,
          "organization": "",
          "location": "",
          "period": "",
          "website": {"url": "", "label": ""},
          "description": ""
        }
      ]
    },
    "certifications": {
      "title": "Certifications",
      "hidden": false,
      "items": [
        {"id": "", "hidden": false, "name": "", "issuer": "", "date": "", "summary": ""}
      ]
    }
  },
  "customSections": [],
  "metadata": {
    "template": "rhyhorn"
  }
}
"""

GENERAL_RULES = """
General rules:

- Extract information ONLY from the provided resume text. Never invent employers,
  dates, titles, schools, skills, certifications, or metrics that are not present
  in the text.
- If a field is missing from the source text, use an empty string, empty array,
  or the given default (e.g. "hidden": false) as appropriate. Do not guess.
- Every item inside experience/education/skills/projects/languages/volunteer/
  certifications arrays MUST include a unique "id" field: generate a short random
  alphanumeric string (8-12 characters) for each one.
- "hidden" fields must always be false for extracted content, at both the
  section level and the item level - the candidate is choosing to include it.
- "description" (experience, education, projects, volunteer) and "content"
  (summary) fields must be simple HTML: wrap plain paragraphs in <p>...</p> and
  wrap bullet points in <ul><li>...</li></ul>. Do not use any other HTML tags.
  This matches the rich-text format the rest of the application expects.
- Only include sections/items that have real content in the source text - do not
  emit empty placeholder items.
- Preserve the candidate's own wording where reasonable; light cleanup of
  formatting artifacts from PDF extraction (broken line breaks, stray bullet
  characters) is fine, but do not rewrite or embellish the content.
- Dates/periods should be kept in the format they appear in the source text
  (e.g. "01/2025 - 08/2025" or "2022 - Present").
- A PDF upload cannot reliably produce a re-hostable profile photo, so "picture"
  must always be returned exactly as shown in the structure above
  ("hidden": true, "url": ""). Do not attempt to describe or reference an image.
- "basics.website" is the candidate's primary link (e.g. LinkedIn) if present in
  the text; additional links (e.g. GitHub, a portfolio site) go into
  "basics.customFields", one entry per link, with a short "text" label and the
  "link" URL. Leave "icon" as an empty string.
- "customSections" must be an empty array.
- "metadata" must be returned exactly as shown in the structure above
  ("template": "rhyhorn") - it is otherwise filled in by the application, not by
  you.
- Return raw JSON only. Do not wrap the JSON in markdown or code fences. Do not
  add any text before or after the JSON.
"""


def build_resume_parsing_prompt() -> str:
    return f"""
{SYSTEM_ROLE}

{JSON_STRUCTURE}

{GENERAL_RULES}
"""
