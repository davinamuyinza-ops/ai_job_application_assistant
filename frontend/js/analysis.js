import { apiJson } from "./api.js";
import { state } from "./state.js";
import { goToView, setStep, showStatusMessage } from "./ui.js";

export async function analyzeJob() {
    try {
        document.getElementById("analyzeButton").disabled = true;

        const jobDescription = document.getElementById("jobDescription").value;
        state.jobDescription = jobDescription;

        if (!state.resumeJson) {
            document.getElementById("analysisResults").textContent =
                "Please upload your resume first.";

            return;
        }

        document.getElementById("analysisResults").textContent =
            "Analyzing job description...";

        goToView("analysisView");
        setStep(2);

        const data = await apiJson("/analyze-job", {
            method: "POST",
            body: JSON.stringify({
                job_description: jobDescription,
                resume_json: state.resumeJson,
            }),
        });

        state.jobAnalysis = data;

        document.getElementById("analysisResults").innerHTML = `
            <div class="analysis-dashboard">

                <div class="score-circle">
                    <span>${data.match_analysis.match_score}%</span>
                    <p>Match Score</p>
                </div>

                <div class="analysis-info-card">
                    <h3>Priority</h3>
                    <p>${data.decision.priority}</p>
                </div>

                <div class="analysis-info-card">
                    <h3>Should Apply</h3>
                    <p>${data.decision.should_apply}</p>
                </div>

                <div class="analysis-info-card">
                    <h3>Confidence</h3>
                    <p>${data.decision.confidence}%</p>
                </div>

                <div class="analysis-reason">
                    <h3>Main Reason</h3>
                    <p>${data.decision.reason}</p>
                </div>

            </div>
        `;

    } catch (error) {
        console.log(error);

        document.getElementById("analysisResults").textContent =
            "Something went wrong while analyzing the job.";
    } finally {
        document.getElementById("analyzeButton").disabled = false;
    }
}

export async function extractJobFromUrl() {
    try {
        document.getElementById("extractButton").disabled = true;

        const jobUrl = document.getElementById("jobLink").value;

        document.getElementById("jobDescription").value =
            "Extracting job description from URL...";

        const data = await apiJson("/extract-job", {
            method: "POST",
            body: JSON.stringify({ job_url: jobUrl }),
        });

        document.getElementById("jobDescription").value = data.job_text;

        showStatusMessage("Job description extracted successfully.");

    } catch (error) {
        console.log(error);

        document.getElementById("jobDescription").value = "";

        showStatusMessage("Could not extract job description from this URL.");

    } finally {
        document.getElementById("extractButton").disabled = false;
    }
}
