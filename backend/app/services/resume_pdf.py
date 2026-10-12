from pathlib import Path

from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "resume_templates"

ALLOWED_TEMPLATES = {"rhyhorn", "sidebar", "minimal"}

_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_resume_html(resume_json: dict, template: str) -> str:
    if template not in ALLOWED_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown template '{template}'. Choose one of: {', '.join(sorted(ALLOWED_TEMPLATES))}",
        )

    jinja_template = _jinja_env.get_template(f"{template}.html")
    return jinja_template.render(resume=resume_json)


def render_resume_pdf(resume_json: dict, template: str) -> bytes:
    html_content = render_resume_html(resume_json, template)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content, wait_until="load")
            pdf_bytes = page.pdf(print_background=True, prefer_css_page_size=True)
            browser.close()
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to render resume PDF",
                "message": str(error),
            },
        )

    return pdf_bytes
