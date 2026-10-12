"""
One-off dev tool: renders each resume template with a generic placeholder
resume and screenshots the top portion, producing the card thumbnails shown
in the frontend's template picker.

Run manually whenever a template's visual design changes:
    .venv/Scripts/python.exe backend/scripts/generate_template_thumbnails.py
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from playwright.sync_api import sync_playwright  # noqa: E402

from app.services.resume_pdf import ALLOWED_TEMPLATES, render_resume_html  # noqa: E402

OUTPUT_DIR = BACKEND_DIR.parent / "frontend" / "images" / "templates"

PLACEHOLDER_RESUME = {
    "picture": {
        "hidden": False,
        "url": "https://ui-avatars.com/api/?name=Jordan+Lee&size=300&background=0F3381&color=fff",
    },
    "basics": {
        "name": "Jordan Lee",
        "headline": "Product Designer",
        "email": "jordan.lee@example.com",
        "phone": "+1 555 0100",
        "location": "Austin, TX",
        "website": {"url": "https://linkedin.com/in/example", "label": "Linkedin"},
        "customFields": [
            {"id": "1", "icon": "", "text": "Portfolio", "link": "https://example.com"}
        ],
    },
    "summary": {
        "title": "Summary",
        "hidden": False,
        "content": (
            "<p>Product designer with 5+ years building user-centered interfaces for "
            "web and mobile products. Focused on design systems, accessibility, and "
            "close collaboration with engineering teams.</p>"
        ),
    },
    "sections": {
        "experience": {
            "title": "Experience",
            "hidden": False,
            "items": [
                {
                    "id": "1",
                    "hidden": False,
                    "company": "Northwind Studio",
                    "position": "Senior Product Designer",
                    "location": "Remote",
                    "period": "2022 - Present",
                    "website": {"url": "", "label": ""},
                    "description": (
                        "<ul><li><p>Led redesign of the core onboarding flow, "
                        "improving completion rate by 18%.</p></li>"
                        "<li><p>Built and maintained the company's design system "
                        "used across five product teams.</p></li></ul>"
                    ),
                },
                {
                    "id": "2",
                    "hidden": False,
                    "company": "Bright Labs",
                    "position": "Product Designer",
                    "location": "Austin, TX",
                    "period": "2019 - 2022",
                    "website": {"url": "", "label": ""},
                    "description": (
                        "<ul><li><p>Designed and shipped features for a B2B "
                        "analytics dashboard used by 10k+ customers.</p></li></ul>"
                    ),
                },
            ],
        },
        "education": {
            "title": "Education",
            "hidden": False,
            "items": [
                {
                    "id": "1",
                    "hidden": False,
                    "school": "University of Texas at Austin",
                    "degree": "B.S.",
                    "area": "Human-Computer Interaction",
                    "grade": "",
                    "location": "",
                    "period": "2015 - 2019",
                    "website": {"url": "", "label": ""},
                    "description": "",
                }
            ],
        },
        "projects": {"title": "Projects", "hidden": False, "items": []},
        "skills": {
            "title": "Skills",
            "hidden": False,
            "items": [
                {
                    "id": "1",
                    "hidden": False,
                    "name": "Design",
                    "proficiency": "",
                    "level": 0,
                    "keywords": ["Figma", "Prototyping", "Design Systems", "Accessibility"],
                },
                {
                    "id": "2",
                    "hidden": False,
                    "name": "Collaboration",
                    "proficiency": "",
                    "level": 0,
                    "keywords": ["User Research", "Cross-functional Leadership"],
                },
            ],
        },
        "languages": {
            "title": "Languages",
            "hidden": False,
            "items": [
                {"id": "1", "hidden": False, "language": "English", "fluency": "Native", "level": 5}
            ],
        },
        "volunteer": {"title": "Volunteering", "hidden": False, "items": []},
        "certifications": {"title": "Certifications", "hidden": False, "items": []},
    },
    "customSections": [],
    "metadata": {"template": "rhyhorn"},
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        for template in sorted(ALLOWED_TEMPLATES):
            html_content = render_resume_html(PLACEHOLDER_RESUME, template)

            page = browser.new_page(viewport={"width": 600, "height": 780}, device_scale_factor=2)
            page.set_content(html_content, wait_until="load")

            output_path = OUTPUT_DIR / f"{template}.png"
            page.screenshot(path=str(output_path))
            page.close()

            print(f"Wrote {output_path}")

        browser.close()


if __name__ == "__main__":
    main()
