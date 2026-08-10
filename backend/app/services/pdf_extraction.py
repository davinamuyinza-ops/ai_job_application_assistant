import io
import json

import pdfplumber
from fastapi import HTTPException

from app.services.ai_client import client, clean_ai_json
from prompts.resume_parsing_prompt import build_resume_parsing_prompt


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Could not read PDF file",
                "message": str(error)
            }
        )

    text = "\n".join(pages_text).strip()

    if not text:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "No extractable text found in PDF",
                "message": "The PDF may be a scanned image rather than a text-based document."
            }
        )

    return text


def parse_resume_pdf_to_json(file_bytes: bytes) -> dict:
    resume_text = extract_text_from_pdf(file_bytes)

    response = None

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0,
            input=[
                {
                    "role": "system",
                    "content": build_resume_parsing_prompt()
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {"resume_text": resume_text},
                        ensure_ascii=False
                    )
                }
            ]
        )

        raw_output = response.output_text
        cleaned_output = clean_ai_json(raw_output)
        return json.loads(cleaned_output)

    except json.JSONDecodeError as exc:
        raw_output = response.output_text if response else "No response received"

        raise HTTPException(
            status_code=500,
            detail={
                "error": "AI returned invalid JSON while parsing the PDF resume",
                "message": str(exc),
                "raw_response": raw_output
            }
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected backend error while parsing the PDF resume",
                "message": str(error)
            }
        )
