import { apiFetch, apiJson } from "./api.js";
import { state } from "./state.js";
import { showStatusMessage } from "./ui.js";

export async function loadMasterResume() {
    try {
        const data = await apiJson("/master-resume");
        state.resumeJson = data.resume_json;
    } catch (error) {
        state.resumeJson = null;
    }
}

export async function saveMasterResumeJson(resumeJson, sourceType = "json_upload") {
    const data = await apiJson("/master-resume", {
        method: "PUT",
        body: JSON.stringify({ resume_json: resumeJson, source_type: sourceType }),
    });

    state.resumeJson = data.resume_json;

    return data;
}

export async function uploadResumeJsonFile(file) {
    const fileText = await file.text();
    const resumeJson = JSON.parse(fileText);

    await saveMasterResumeJson(resumeJson, "json_upload");

    showStatusMessage("Resume uploaded and saved successfully.");
}

export async function parseResumePdf(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiFetch("/master-resume/parse-pdf", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        const message = detail?.detail?.error || detail?.detail || "Could not parse that PDF.";
        throw new Error(message);
    }

    const data = await response.json();
    state.pendingParsedResume = data.resume_json;

    return data.resume_json;
}

export async function confirmParsedResume() {
    if (!state.pendingParsedResume) {
        return;
    }

    await saveMasterResumeJson(state.pendingParsedResume, "pdf_upload");

    state.pendingParsedResume = null;

    showStatusMessage("Master resume saved successfully.");
}

export function discardParsedResume() {
    state.pendingParsedResume = null;
}
