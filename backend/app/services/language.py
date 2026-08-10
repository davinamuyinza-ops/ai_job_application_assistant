from langdetect import DetectorFactory, detect_langs

DetectorFactory.seed = 0


def detect_target_language(job_description: str) -> str:
    text = job_description.strip()

    if not text:
        return "English"

    try:
        detected_languages = detect_langs(text)

        print("Language detection result:", detected_languages)

        german_probability = 0
        english_probability = 0

        for language in detected_languages:
            if language.lang == "de":
                german_probability = language.prob

            if language.lang == "en":
                english_probability = language.prob

        if german_probability >= 0.25:
            return "German"

        if english_probability >= 0.50:
            return "English"

        return "English"

    except Exception as error:
        print("Language detection failed:", error)
        return "English"
