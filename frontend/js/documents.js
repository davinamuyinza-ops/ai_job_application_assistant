import { apiJson } from "./api.js";
import { typewriter } from "./animation.js";
import { loadResumeIntoEditor } from "./resumeEditor.js";
import { state } from "./state.js";
import { goToView, refreshGating, showStatusMessage } from "./ui.js";

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

        document.getElementById("resumeCardBody").innerHTML = `
            <p class="section-description">Your tailored resume is ready to review.</p>
            <button id="goToResumeEditorButton">Edit Resume</button>
        `;

        document.getElementById("goToResumeEditorButton").addEventListener("click", () => {
            goToView("resumeEditorView");
        });

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

        typewriter(document.getElementById("coverLetterResults"), data.cover_letter);

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
