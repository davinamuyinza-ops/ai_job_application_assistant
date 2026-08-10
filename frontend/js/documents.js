import { apiJson } from "./api.js";
import { state } from "./state.js";
import { goToView, setStep, showStatusMessage } from "./ui.js";

export async function generateResume() {
    try {
        document.getElementById("resumeButton").disabled = true;

        document.getElementById("resumeResults").innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                Generating tailored resume...
            </div>
        `;

        goToView("documentsView");
        setStep(3);

        const data = await apiJson("/tailor-resume", {
            method: "POST",
            body: JSON.stringify({
                job_description: state.jobDescription,
                resume_json: state.resumeJson,
                job_analysis: state.jobAnalysis,
            }),
        });

        state.tailoredResume = data.tailored_resume_json || data;

        document.getElementById("resumeResults").textContent =
            "Tailored resume generated successfully. Ready for download.";

    } catch (error) {
        console.log(error);

        document.getElementById("resumeResults").textContent =
            "Something went wrong while generating the tailored resume.";
    } finally {
        document.getElementById("resumeButton").disabled = false;
    }
}

export async function generateCoverLetter() {
    try {
        document.getElementById("coverLetterButton").disabled = true;

        document.getElementById("coverLetterResults").innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                Generating cover letter...
            </div>
        `;

        goToView("documentsView");
        setStep(4);

        const data = await apiJson("/generate-cover-letter", {
            method: "POST",
            body: JSON.stringify({
                job_description: state.jobDescription,
                resume_json: state.resumeJson,
                job_analysis: state.jobAnalysis,
            }),
        });

        state.coverLetter = data;

        document.getElementById("coverLetterResults").textContent = data.cover_letter;

    } catch (error) {
        console.log(error);

        document.getElementById("coverLetterResults").textContent =
            "Something went wrong while generating the cover letter.";
    } finally {
        document.getElementById("coverLetterButton").disabled = false;
    }
}

export function downloadResumeJson() {
    if (!state.tailoredResume) {
        showStatusMessage("No tailored resume available yet.");
        return;
    }

    const jsonString = JSON.stringify(state.tailoredResume, null, 2);

    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "tailored_resume.json";
    link.click();

    showStatusMessage("Tailored resume downloaded successfully.");

    URL.revokeObjectURL(url);
}

export function copyCoverLetter() {
    if (!state.coverLetter) {
        showStatusMessage("No cover letter available yet.");
        return;
    }

    navigator.clipboard.writeText(state.coverLetter.cover_letter);

    showStatusMessage("Cover letter copied successfully.");
}
