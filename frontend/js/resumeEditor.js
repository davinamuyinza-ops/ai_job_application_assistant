import { apiJson } from "./api.js";
import { getAccessToken } from "./auth.js";
import { RESUME_EDITOR_ORIGIN, RESUME_EDITOR_URL } from "./config.js";
import { state } from "./state.js";
import { refreshGating, showStatusMessage } from "./ui.js";

function getEditorWindow() {
    return document.getElementById("resumeEditorFrame")?.contentWindow || null;
}

// The editor has no login of its own: it borrows this app's Supabase session
// by being handed the access token, and its backend verifies that same token.
export async function sendAuthTokenToEditor() {
    const editorWindow = getEditorWindow();
    const token = await getAccessToken();

    if (!editorWindow || !token) {
        return;
    }

    editorWindow.postMessage({ type: "auth-token", token }, RESUME_EDITOR_ORIGIN);
}

export function loadResumeIntoEditor(resumeJson) {
    const frame = document.getElementById("resumeEditorFrame");

    if (!frame) {
        return;
    }

    async function handleLoad() {
        frame.removeEventListener("load", handleLoad);

        // Token first: the editor starts rendering previews as soon as it
        // has a resume, and those calls need the token already in place.
        await sendAuthTokenToEditor();

        frame.contentWindow.postMessage(
            { type: "load-resume", resume: resumeJson, jobDescription: state.jobDescription || null },
            RESUME_EDITOR_ORIGIN,
        );
    }

    frame.addEventListener("load", handleLoad);
    // Force a fresh navigation (not a same-URL no-op) so the editor always
    // starts clean with the resume just handed to it, even if it was
    // already open from an earlier visit.
    frame.src = `${RESUME_EDITOR_URL}?t=${Date.now()}`;
}

async function saveEditedResume(resume) {
    if (!state.currentApplicationId) {
        return;
    }

    try {
        await apiJson(`/applications/${state.currentApplicationId}/documents`, {
            method: "PUT",
            body: JSON.stringify({ tailored_resume: resume }),
        });
    } catch (error) {
        console.log(error);
        showStatusMessage("Could not save your resume edits to this application.");
    }
}

export function initResumeEditorBridge() {
    window.addEventListener("message", (event) => {
        if (event.origin !== RESUME_EDITOR_ORIGIN) {
            return;
        }

        if (event.data?.type === "resume-updated" && event.data.resume) {
            state.tailoredResume = event.data.resume;
            refreshGating();
            saveEditedResume(event.data.resume);
        }

        // The editor asks for a fresh token on startup and whenever its
        // backend rejects the one it holds (e.g. after hourly expiry).
        if (event.data?.type === "editor-ready" || event.data?.type === "token-needed") {
            sendAuthTokenToEditor();
        }
    });
}
