import json

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.resume import ResumeTailoringResponse
from app.services.ai_client import build_language_lock, client, clean_ai_json
from app.services.language import detect_target_language
from prompts.resume_tailoring_prompt import build_resume_tailoring_prompt


def tailor_resume_json(job_description: str, resume_json: dict, job_analysis: dict):
    response = None
    tailored_json = None

    target_language = detect_target_language(job_description)
    print("Resume target language:", target_language)

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0,
            input=[
                {
                    "role": "system",
                    "content": build_resume_tailoring_prompt()
                },
                {
                    "role": "developer",
                    "content": build_language_lock(target_language, "tailored resume")
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "target_language": target_language,
                            "job_description": job_description,
                            "job_analysis": job_analysis,
                            "resume_json": resume_json
                        },
                        ensure_ascii=False
                    )
                }
            ]
        )

        raw_output = response.output_text
        cleaned_output = clean_ai_json(raw_output)
        tailored_json = json.loads(cleaned_output)

        validated_result = ResumeTailoringResponse.model_validate(tailored_json)
        validated_result.tailored_resume_json["metadata"] = resume_json.get("metadata")
        validated_result.tailored_resume_json["customSections"] = resume_json.get("customSections", [])
        validated_result.tailored_resume_json["picture"] = resume_json.get("picture")
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
                "parsed_json": tailored_json
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
