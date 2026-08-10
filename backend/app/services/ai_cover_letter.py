import json

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.cover_letter import CoverLetterGenerationResponse
from app.services.ai_client import build_language_lock, client, clean_ai_json
from app.services.language import detect_target_language
from prompts.cover_letter_prompt import build_cover_letter_generation_prompt


def generate_cover_letter(job_description: str, resume_json: dict, job_analysis: dict):
    response = None
    cover_letter_json = None

    target_language = detect_target_language(job_description)
    print("Cover letter target language:", target_language)

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0,
            input=[
                {
                    "role": "system",
                    "content": build_cover_letter_generation_prompt()
                },
                {
                    "role": "developer",
                    "content": build_language_lock(target_language, "cover letter")
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "target_language": target_language,
                            "job_description": job_description,
                            "resume_json": resume_json,
                            "job_analysis": job_analysis,
                            "required_output_structure": {
                                "cover_letter": "",
                                "key_points_used": [],
                                "tone_used": ""
                            }
                        },
                        ensure_ascii=False
                    )
                }
            ]
        )

        raw_output = response.output_text
        cleaned_output = clean_ai_json(raw_output)
        cover_letter_json = json.loads(cleaned_output)

        validated_result = CoverLetterGenerationResponse.model_validate(cover_letter_json)
        return validated_result

    except json.JSONDecodeError as exc:
        raw_output = response.output_text if response else "No response received"

        raise HTTPException(
            status_code=500,
            detail={
                "error": "AI returned invalid JSON",
                "message": str(exc),
                "raw_response": raw_output
            }
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "AI response failed validation",
                "message": exc.errors(),
                "parsed_json": cover_letter_json
            }
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected backend error",
                "message": str(error)
            }
        )
