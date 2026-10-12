import re

from langdetect import DetectorFactory, detect_langs

DetectorFactory.seed = 0

# Section/summary titles are short strings (often 1-3 words), which langdetect
# handles poorly and unreliably. A tailored resume also mostly consists of long
# English or German body text, so a handful of mistranslated titles barely move
# a bulk statistical language check - exactly the failure mode observed in
# practice (German section headings sitting next to English bullet content).
# A small keyword list catches this specific, common defect far more reliably
# than statistical detection on short strings.
#
# "engagement" is deliberately absent from either list: it's a legitimate
# loanword in German too (the real reference resume this was built against
# uses "Freiwilliges Engagement" as an actual German title), so it isn't a
# reliable signal in either direction.
GERMAN_TITLE_INDICATORS = [
    "berufserfahrung", "erfahrung", "bildung", "ausbildung", "projekte",
    "fähigkeiten", "kenntnisse", "sprachen", "freiwillig",
    "zertifi", "auszeichnung", "veröffentlichung", "interessen", "referenzen",
    "profil", "zusammenfassung",
]

ENGLISH_TITLE_INDICATORS = [
    "experience", "education", "projects", "skills", "languages",
    "volunteering", "volunteer", "certification", "award", "publication",
    "interest", "reference", "summary", "profile",
]

# Fields whose values are proper nouns, dates, or otherwise not translatable -
# excluded from both the title check and the body-text check.
_PROPER_NOUN_KEYS = {"company", "school", "organization", "name", "issuer", "url", "link", "location", "grade", "period", "email", "phone", "id", "hidden", "icon"}


def _contains_indicator(text: str, indicator: str) -> bool:
    # Most indicators are deliberately used as prefixes/stems to catch German
    # inflected forms (e.g. "freiwillig" also matching "Freiwillige",
    # "zertifi" also matching "Zertifikate"/"zertifiziert"), so this is plain
    # substring matching by default - except "profil", where that same
    # approach produces a false positive: German "profil" is also the first
    # six letters of English "profile", so a real English title would
    # otherwise incorrectly flag as German.
    if indicator == "profil":
        return re.search(r"profil(?!e)", text) is not None

    return indicator in text


def _collect_titles(resume_json: dict) -> list[str]:
    titles = []

    summary = resume_json.get("summary") or {}
    if summary.get("title"):
        titles.append(summary["title"])

    sections = resume_json.get("sections") or {}
    for section in sections.values():
        if isinstance(section, dict) and section.get("title"):
            titles.append(section["title"])

    return titles


def _collect_body_text(resume_json: dict) -> str:
    chunks = []

    summary = resume_json.get("summary") or {}
    if summary.get("content"):
        chunks.append(summary["content"])

    sections = resume_json.get("sections") or {}
    for section in sections.values():
        if not isinstance(section, dict):
            continue

        for item in section.get("items", []) or []:
            if not isinstance(item, dict):
                continue

            for key, value in item.items():
                if key in _PROPER_NOUN_KEYS or key == "keywords":
                    continue
                if isinstance(value, str) and value.strip():
                    chunks.append(value)

    return "\n".join(chunks)


def titles_in_wrong_language(resume_json: dict, target_language: str) -> bool:
    indicators = ENGLISH_TITLE_INDICATORS if target_language == "German" else GERMAN_TITLE_INDICATORS

    for title in _collect_titles(resume_json):
        lowered = title.lower()
        if any(_contains_indicator(lowered, indicator) for indicator in indicators):
            return True

    return False


def body_text_in_wrong_language(resume_json: dict, target_language: str) -> bool:
    text = _collect_body_text(resume_json).strip()

    if not text:
        return False

    try:
        detected = detect_langs(text)
    except Exception:
        return False

    wrong_code = "de" if target_language == "English" else "en"

    for lang in detected:
        if lang.lang == wrong_code and lang.prob >= 0.15:
            return True

    return False


def language_check_passes(resume_json: dict, target_language: str) -> bool:
    if titles_in_wrong_language(resume_json, target_language):
        return False

    if body_text_in_wrong_language(resume_json, target_language):
        return False

    return True
