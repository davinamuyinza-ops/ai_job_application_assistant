import { apiJson } from "./api.js";
import { typewriter } from "./animation.js";
import { loadResumeIntoEditor } from "./resumeEditor.js";
import { state } from "./state.js";
import { goToView, refreshGating, showStatusMessage } from "./ui.js";

export function showResumeReady() {
    document.getElementById("resumeCardBody").innerHTML = `
        <p class="section-description">Your tailored resume is ready to review.</p>
        <button id="goToResumeEditorButton">Edit Resume</button>
    `;

    document.getElementById("goToResumeEditorButton").addEventListener("click", () => {
        goToView("resumeEditorView");
    });
}

export function showResumeMissing() {
    document.getElementById("resumeCardBody").innerHTML = `
        <p class="section-description">No tailored resume was saved for this application.</p>
    `;
}

export function showCoverLetter(text, { animate = false } = {}) {
    const target = document.getElementById("coverLetterResults");

    if (!text) {
        target.textContent = "No cover letter was saved for this application.";
        return;
    }

    if (animate) {
        typewriter(target, text);
    } else {
        target.textContent = text;
    }
}

export async function generateResume() {
    try {
        document.getElementById("resumeCardBody").innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                Generating tailored resume...
            </div>
        `;

        const data = await apiJson("/tailor-resume", {
            method: "POST",
            body: JSON.stringify({
                job_description: state.jobDescription,
                resume_json: state.resumeJson,
                job_analysis: state.jobAnalysis,
            }),
        });

        state.tailoredResume = data.tailored_resume_json || data;
        loadResumeIntoEditor(state.tailoredResume);
        refreshGating();

        showResumeReady();

        return { ok: true, message: "Tailored resume generated." };

    } catch (error) {
        console.log(error);

        document.getElementById("resumeCardBody").innerHTML = `
            <p class="section-description">Something went wrong while generating the tailored resume.</p>
        `;

        return { ok: false, message: "Something went wrong while generating the tailored resume." };
    }
}

export async function generateCoverLetter() {
    try {
        document.getElementById("coverLetterResults").innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                Generating cover letter...
            </div>
        `;

        const data = await apiJson("/generate-cover-letter", {
            method: "POST",
            body: JSON.stringify({
                job_description: state.jobDescription,
                resume_json: state.resumeJson,
                job_analysis: state.jobAnalysis,
                personal_motivation: state.personalMotivation || undefined,
            }),
        });

        state.coverLetter = data;
        refreshGating();

        showCoverLetter(data.cover_letter, { animate: true });

        return { ok: true, message: "Cover letter generated." };

    } catch (error) {
        console.log(error);

        document.getElementById("coverLetterResults").textContent =
            "Something went wrong while generating the cover letter.";

        return { ok: false, message: "Something went wrong while generating the cover letter." };
    }
}

export function copyCoverLetter() {
    if (!state.coverLetter) {
        showStatusMessage("No cover letter available yet.");
        return;
    }

    navigator.clipboard.writeText(state.coverLetter.cover_letter);

    showStatusMessage("Cover letter copied successfully.");
}
