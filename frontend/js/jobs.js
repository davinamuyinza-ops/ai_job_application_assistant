import { apiJson } from "./api.js";
import { state } from "./state.js";
import { showStatusMessage } from "./ui.js";

export function renderPromisingJobs() {
    const list = document.getElementById("promisingJobsList");

    list.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="empty-state">
                    No promising jobs found yet.
                </div>
            </td>
        </tr>
    `;

    state.promisingJobs.forEach((job, index) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${job.title}</td>
            <td>${job.company}</td>
            <td>${job.location}</td>
            <td>${job.reason}</td>
            <td>
                <a href="${job.link}" target="_blank">
                    Open
                </a>
            </td>
            <td>
                <button onclick="usePromisingJob(${index})">
                    Use Job
                </button>
            </td>
        `;

        list.appendChild(row);
    });
}

export function usePromisingJob(index) {
    const selectedJob = state.promisingJobs[index];

    document.getElementById("jobLink").value = selectedJob.link;

    showStatusMessage("Job link added successfully.");
}

export async function findJobs() {
    try {
        if (!state.resumeJson) {
            showStatusMessage("Upload your resume first.");
            return;
        }

        document.getElementById("promisingJobsList").innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="loading-state">
                        <div class="loading-spinner"></div>
                        Searching for matching jobs...
                    </div>
                </td>
            </tr>
        `;

        const data = await apiJson("/search-jobs", {
            method: "POST",
            body: JSON.stringify({ resume_json: state.resumeJson }),
        });

        if (!data.jobs) {
            console.log(data);

            document.getElementById("promisingJobsList").innerHTML = `
                <tr>
                    <td colspan="6">
                        Backend did not return job results.
                    </td>
                </tr>
            `;

            return;
        }

        state.promisingJobs = data.jobs;

        renderPromisingJobs();

        showStatusMessage("Matching jobs found successfully.");

    } catch (error) {
        console.log(error);

        document.getElementById("promisingJobsList").innerHTML = `
            <tr>
                <td colspan="6">
                    Something went wrong while searching for jobs.
                </td>
            </tr>
        `;
    }
}
