import json

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.resume import ResumeTailoringResponse
from app.services.ai_client import build_language_lock, client, clean_ai_json
from app.services.language import detect_target_language
from app.services.language_check import language_check_passes
from prompts.resume_tailoring_prompt import build_resume_tailoring_prompt


def _attempt_language_correction(messages: list, raw_output: str, target_language: str):
    """
    One bounded corrective retry: replay the conversation with the flawed
    output added back as the assistant's turn, and ask the model to re-audit
    and fix only the remaining language violations. Returns a validated
    ResumeTailoringResponse on success, or None if the retry itself fails
    (caller falls back to the original result rather than blocking the user).
    """
    try:
        correction_messages = messages + [
            {"role": "assistant", "content": raw_output},
            {
                "role": "developer",
                "content": f"""
                    LANGUAGE CHECK FAILED.

                    Your previous output above still contains text that is not fully
                    {target_language}. This includes section titles (e.g. "title" fields)
                    and/or descriptive body text that were left in the wrong language.

                    Re-audit the ENTIRE JSON you just returned, field by field, against
                    the SCHEMA FIELD REFERENCE and TARGET LANGUAGE RULES in the system
                    prompt. Rewrite every field marked TRANSLATE that is not fully in
                    {target_language}. Do NOT change anything else - keep all content,
                    structure, ids, and prior decisions identical except for fixing the
                    remaining language violations.

                    Return the complete corrected JSON in the exact same format as before.
                    """
            },
        ]

        retry_response = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0,
            input=correction_messages,
        )

        retry_raw_output = retry_response.output_text
        retry_cleaned = clean_ai_json(retry_raw_output)
        retry_json = json.loads(retry_cleaned)

        return ResumeTailoringResponse.model_validate(retry_json)

    except Exception as error:
        print("Language correction retry failed, keeping original result:", error)
        return None


def tailor_resume_json(job_description: str, resume_json: dict, job_analysis: dict):
    response = None
    tailored_json = None

    target_language = detect_target_language(job_description)
    print("Resume target language:", target_language)

    messages = [
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

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0,
            input=messages,
        )

        raw_output = response.output_text
        cleaned_output = clean_ai_json(raw_output)
        tailored_json = json.loads(cleaned_output)

        validated_result = ResumeTailoringResponse.model_validate(tailored_json)

        if not language_check_passes(validated_result.tailored_resume_json, target_language):
            print("Language check failed, attempting one corrective retry")
            corrected_result = _attempt_language_correction(messages, raw_output, target_language)

            if corrected_result is not None:
                if language_check_passes(corrected_result.tailored_resume_json, target_language):
                    print("Corrective retry fixed the language check")
                else:
                    print("Corrective retry ran but language check still fails - returning it anyway")
                validated_result = corrected_result
            else:
                print("Corrective retry unavailable - returning original (uncorrected) result")

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
