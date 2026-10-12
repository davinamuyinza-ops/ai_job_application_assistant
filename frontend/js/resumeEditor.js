import { RESUME_EDITOR_ORIGIN, RESUME_EDITOR_URL } from "./config.js";
import { state } from "./state.js";
import { refreshGating } from "./ui.js";

export function loadResumeIntoEditor(resumeJson) {
    const frame = document.getElementById("resumeEditorFrame");

    if (!frame) {
        return;
    }

    function handleLoad() {
        frame.contentWindow.postMessage(
            { type: "load-resume", resume: resumeJson, jobDescription: state.jobDescription || null },
            RESUME_EDITOR_ORIGIN,
        );
        frame.removeEventListener("load", handleLoad);
    }

    frame.addEventListener("load", handleLoad);
    // Force a fresh navigation (not a same-URL no-op) so the editor always
    // starts clean with the resume just handed to it, even if it was
    // already open from an earlier visit.
    frame.src = `${RESUME_EDITOR_URL}?t=${Date.now()}`;
}

export function initResumeEditorBridge() {
    window.addEventListener("message", (event) => {
        if (event.origin !== RESUME_EDITOR_ORIGIN) {
            return;
        }

        if (event.data?.type === "resume-updated" && event.data.resume) {
            state.tailoredResume = event.data.resume;
            refreshGating();
        }
    });
}
