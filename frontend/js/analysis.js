import { apiJson } from "./api.js";
import { celebrate } from "./animation.js";
import { state } from "./state.js";
import { goToView, refreshGating, showStatusMessage } from "./ui.js";

const STRONG_MATCH_THRESHOLD = 70;

function animateScoreCircle(circle, targetScore, duration = 800) {
    const span = circle.querySelector("span");
    const start = performance.now();

    function tick(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(targetScore * eased);

        span.textContent = `${current}%`;
        circle.style.background = `conic-gradient(#2563eb ${current}%, #dbe3f0 0)`;

        if (progress < 1) {
            requestAnimationFrame(tick);
        } else {
            const bounce = circle.animate(
                [
                    { transform: "scale(1)" },
                    { transform: "scale(1.08)" },
                    { transform: "scale(1)" },
                ],
                { duration: 350, easing: "cubic-bezier(0.34, 1.56, 0.64, 1)" },
            );

            // A strong match is a genuine "good news" moment, so it shares the
            // same celebration language used later when Continue succeeds -
            // one consistent reward motif instead of two unrelated effects.
            if (targetScore >= STRONG_MATCH_THRESHOLD) {
                bounce.addEventListener("finish", () => celebrate(circle));
            }
        }
    }

    requestAnimationFrame(tick);
}

export async function analyzeJob() {
    try {
        document.getElementById("analyzeButton").disabled = true;

        const jobDescription = document.getElementById("jobDescription").value;
        state.jobDescription = jobDescription;

        if (!state.resumeJson) {
            showStatusMessage("Please upload your resume first.");

            return;
        }

        document.getElementById("postAnalysisActions").style.display = "none";

        document.getElementById("analysisResults").innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                Analyzing job description...
            </div>
        `;

        goToView("analysisView");

        const data = await apiJson("/analyze-job", {
            method: "POST",
            body: JSON.stringify({
                job_description: jobDescription,
                resume_json: state.resumeJson,
            }),
        });

        state.jobAnalysis = data;
        refreshGating();

        document.getElementById("analysisResults").innerHTML = `
            <div class="analysis-dashboard">

                <div class="score-circle">
                    <span>0%</span>
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

        animateScoreCircle(document.querySelector(".score-circle"), data.match_analysis.match_score);

        document.getElementById("postAnalysisActions").style.display = "block";

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
