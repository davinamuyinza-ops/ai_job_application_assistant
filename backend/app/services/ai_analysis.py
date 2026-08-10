import json

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.job_analysis import JobAnalysisResponse
from app.services.ai_client import client, clean_ai_json
from app.services.language import detect_target_language
from prompts.analysis_prompt import build_analysis_prompt


def run_full_job_analysis(job_description: str, user_profile: str):
    response = None
    ai_json = None

    target_language = detect_target_language(job_description)
    print("Analysis target language:", target_language)

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0,
            input=[
                {
                    "role": "system",
                    "content": build_analysis_prompt()
                },
                {
                    "role": "developer",
                    "content": f"""
                        TARGET LANGUAGE: {target_language}

                        You must write ALL generated JSON values in {target_language}.

                        The job description language is authoritative.

                        Do not answer in English unless TARGET LANGUAGE is English.

                        If TARGET LANGUAGE is German:
                        - all summaries must be German
                        - all recommendations must be German
                        - all strengths must be German
                        - all gaps must be German
                        - all risks must be German
                        - all workflow recommendations must be German
                        - all CV tailoring plan values must be German
                        - all cover letter plan values must be German

                        JSON keys must stay unchanged.
                        Only JSON values are translated.

                        Return only valid JSON.
                        """
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "target_language": target_language,
                            "job_description": job_description,
                            "profile": user_profile
                        },
                        ensure_ascii=False
                    )
                }
            ]
        )

        raw_output = response.output_text
        cleaned_output = clean_ai_json(raw_output)
        ai_json = json.loads(cleaned_output)

        validated_result = JobAnalysisResponse.model_validate(ai_json)
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
                "parsed_json": ai_json
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
