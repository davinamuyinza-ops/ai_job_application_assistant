import { apiFetch, apiJson } from "./api.js";
import { state } from "./state.js";
import { goToView, showStatusMessage } from "./ui.js";

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
        showStatusMessage("Run a job analysis first.");
        return;
    }

    const payload = {
        company: state.jobAnalysis.core_fields.company,
        role: state.jobAnalysis.core_fields.job_title,
        match_score: state.jobAnalysis.match_analysis.match_score,
        priority: state.jobAnalysis.decision.priority,
        should_apply: String(state.jobAnalysis.decision.should_apply),
        status: "Saved",
        application_date: new Date().toLocaleDateString(),
        job_link: document.getElementById("jobLink").value,
    };

    await apiJson("/save-application", {
        method: "POST",
        body: JSON.stringify(payload),
    });

    showStatusMessage("Application saved successfully.");

    await loadApplicationsFromBackend();

    goToView("applicationsView");
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

        const statusClass = application.status.toLowerCase();

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${application.company}</td>
            <td>${application.role}</td>
            <td>
                <div class="score-cell">
                    <span>${application.matchScore}%</span>
                    <div class="score-bar">
                        <div class="score-fill"
                            style="width: ${application.matchScore}%;">
                        </div>
                    </div>
                </div>
            </td>
            <td>
                <span class="priority-badge ${application.priority.toLowerCase()}">
                    ${application.priority}
                </span>
            </td>
            <td>${application.shouldApply}</td>

            <td>
                <span class="status-badge ${statusClass}">
                    ${application.status}
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

            <td>${application.date}</td>

            <td>
                <button class="action-button delete"
                        onclick="deleteApplication(${application.id})">
                    Delete
                </button>
            </td>
        `;

        list.appendChild(row);
    });
}

export async function updateApplicationStatus(id, newStatus) {
    await apiFetch(`/applications/${id}/status?status=${newStatus}`, {
        method: "PUT",
    });

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

    document.getElementById("totalCount").textContent = total;
    document.getElementById("appliedCount").textContent = applied;
    document.getElementById("interviewCount").textContent = interviews;
    document.getElementById("offerCount").textContent = offers;

    document.getElementById("dashboardTotalCount").textContent = total;
    document.getElementById("dashboardAppliedCount").textContent = applied;
    document.getElementById("dashboardInterviewCount").textContent = interviews;
    document.getElementById("dashboardOfferCount").textContent = offers;
}
