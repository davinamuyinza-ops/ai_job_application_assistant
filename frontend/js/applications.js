import { animateCount, animateWidth } from "./animation.js";
import { apiFetch, apiJson } from "./api.js";
import { showCoverLetter, showResumeMissing, showResumeReady } from "./documents.js";
import { loadResumeIntoEditor } from "./resumeEditor.js";
import { state } from "./state.js";
import { goToView, refreshGating, showStatusMessage } from "./ui.js";

// Company/role/etc. come from AI reading third-party job postings, so they're
// untrusted text and must never be interpolated into innerHTML raw.
function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

export async function loadApplicationsFromBackend() {
    try {
        const data = await apiJson("/applications");

        state.applications = data.map(app => ({
            id: app.id,
            company: app.company,
            role: app.role,
            matchScore: app.match_score,
            priority: app.priority,
            shouldApply: app.should_apply,
            status: app.status,
            date: app.application_date,
            jobLink: app.job_link,
            jobAnalysis: app.job_analysis,
            hasDocuments: Boolean(app.has_tailored_resume || app.has_cover_letter),
        }));

        renderSavedApplications();
        updateDashboardStats();

    } catch (error) {
        console.log(error);

        showStatusMessage("Failed to load applications from database.");
    }
}

export async function saveApplication() {
    if (!state.jobAnalysis) {
        return { ok: false, message: "Run a job analysis first." };
    }

    try {
        const payload = {
            company: state.jobAnalysis.core_fields.company,
            role: state.jobAnalysis.core_fields.job_title,
            match_score: state.jobAnalysis.match_analysis.match_score,
            priority: state.jobAnalysis.decision.priority,
            should_apply: String(state.jobAnalysis.decision.should_apply),
            status: "Saved",
            application_date: new Date().toLocaleDateString(),
            job_link: document.getElementById("jobLink").value,
            job_analysis: state.jobAnalysis,
            // Documents that finished generating before this save are stored
            // with the application so they survive a refresh.
            tailored_resume: state.tailoredResume || null,
            cover_letter: state.coverLetter?.cover_letter || null,
            job_description: state.jobDescription || null,
        };

        const saved = await apiJson("/save-application", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        state.currentApplicationId = saved.id;

        await loadApplicationsFromBackend();
        refreshGating();

        return { ok: true, message: "Application saved." };

    } catch (error) {
        console.log(error);
        return { ok: false, message: "Something went wrong while saving the application." };
    }
}

export function renderSavedApplications() {
    const list = document.getElementById("savedApplicationsList");

    const selectedFilter = document.getElementById("statusFilter").value;
    const sortOption = document.getElementById("sortOption").value;

    list.innerHTML = "";

    let filteredApplications = [...state.applications];

    if (sortOption === "highestScore") {
        filteredApplications.sort((a, b) => b.matchScore - a.matchScore);
    } else if (sortOption === "lowestScore") {
        filteredApplications.sort((a, b) => a.matchScore - b.matchScore);
    } else {
        filteredApplications.reverse();
    }

    filteredApplications.forEach(application => {
        if (selectedFilter !== "All" && application.status !== selectedFilter) {
            return;
        }

        const statusClass = escapeHtml(application.status.toLowerCase());

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${escapeHtml(application.company)}</td>
            <td>${escapeHtml(application.role)}</td>
            <td>
                <div class="score-cell">
                    <span>${Number(application.matchScore)}%</span>
                    <div class="score-bar">
                        <div class="score-fill" data-score="${Number(application.matchScore)}"></div>
                    </div>
                </div>
            </td>
            <td>
                <span class="priority-badge ${escapeHtml(application.priority.toLowerCase())}">
                    ${escapeHtml(application.priority)}
                </span>
            </td>
            <td>${escapeHtml(application.shouldApply)}</td>

            <td>
                <span class="status-badge ${statusClass}">
                    ${escapeHtml(application.status)}
                </span>

                <select onchange="updateApplicationStatus(${application.id}, this.value)">
                    <option value="Saved" ${application.status === "Saved" ? "selected" : ""}>Saved</option>
                    <option value="Applied" ${application.status === "Applied" ? "selected" : ""}>Applied</option>
                    <option value="Interview" ${application.status === "Interview" ? "selected" : ""}>Interview</option>
                    <option value="Rejected" ${application.status === "Rejected" ? "selected" : ""}>Rejected</option>
                    <option value="Offer" ${application.status === "Offer" ? "selected" : ""}>Offer</option>
                    <option value="Accepted" ${application.status === "Accepted" ? "selected" : ""}>Accepted</option>
                </select>
            </td>

            <td>${escapeHtml(application.date)}</td>

            <td>
                ${application.hasDocuments ? `
                <button onclick="openApplicationDocuments(${Number(application.id)})">
                    Open
                </button>` : ""}
                <button class="action-button delete"
                        onclick="deleteApplication(${application.id})">
                    Delete
                </button>
            </td>
        `;

        list.appendChild(row);
    });

    list.querySelectorAll(".score-fill").forEach(fill => {
        animateWidth(fill, Number(fill.dataset.score));
    });
}

export async function openApplicationDocuments(id) {
    try {
        const documents = await apiJson(`/applications/${id}/documents`);
        const application = state.applications.find(app => app.id === id);

        state.currentApplicationId = id;
        state.jobAnalysis = application?.jobAnalysis || state.jobAnalysis;
        state.jobDescription = documents.job_description || "";
        state.tailoredResume = documents.tailored_resume || null;
        state.coverLetter = documents.cover_letter ? { cover_letter: documents.cover_letter } : null;

        if (state.tailoredResume) {
            loadResumeIntoEditor(state.tailoredResume);
            showResumeReady();
        } else {
            showResumeMissing();
        }

        showCoverLetter(documents.cover_letter);

        goToView("documentsView");
    } catch (error) {
        console.log(error);
        showStatusMessage("Could not open the saved documents.");
    }
}

export async function updateApplicationStatus(id, newStatus) {
    try {
        const response = await apiFetch(`/applications/${id}/status?status=${newStatus}`, {
            method: "PUT",
        });

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }
    } catch (error) {
        console.log(error);
        showStatusMessage("Could not update status - re-loading applications.");
        await loadApplicationsFromBackend();
        return;
    }

    const application = state.applications.find(app => app.id === id);

    if (application) {
        application.status = newStatus;
    }

    renderSavedApplications();
    updateDashboardStats();
}

export async function deleteApplication(id) {
    await apiFetch(`/applications/${id}`, { method: "DELETE" });

    state.applications = state.applications.filter(app => app.id !== id);

    renderSavedApplications();
    updateDashboardStats();

    showStatusMessage("Application deleted.");
}

export function updateDashboardStats() {
    const total = state.applications.length;
    const applied = state.applications.filter(app => app.status === "Applied").length;
    const interviews = state.applications.filter(app => app.status === "Interview").length;
    const offers = state.applications.filter(app => app.status === "Offer").length;
    const rejected = state.applications.filter(app => app.status === "Rejected").length;

    animateCount(document.getElementById("totalCount"), total);
    animateCount(document.getElementById("appliedCount"), applied);
    animateCount(document.getElementById("interviewCount"), interviews);
    animateCount(document.getElementById("offerCount"), offers);
    animateCount(document.getElementById("rejectedCount"), rejected);

    animateCount(document.getElementById("dashboardTotalCount"), total);
    animateCount(document.getElementById("dashboardAppliedCount"), applied);
    animateCount(document.getElementById("dashboardInterviewCount"), interviews);
    animateCount(document.getElementById("dashboardOfferCount"), offers);
    animateCount(document.getElementById("dashboardRejectedCount"), rejected);
}
