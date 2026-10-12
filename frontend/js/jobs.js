import { apiJson } from "./api.js";
import { state } from "./state.js";
import { goToView, showStatusMessage } from "./ui.js";

export function renderPromisingJobs() {
    const list = document.getElementById("promisingJobsList");

    if (!state.promisingJobs.length) {
        list.innerHTML = `
            <tr>
                <td colspan="7">
                    <div class="empty-state">
                        No promising jobs found yet.
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    list.innerHTML = "";

    state.promisingJobs.forEach((job, index) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${job.title}</td>
            <td>${job.company}</td>
            <td>${job.location}</td>
            <td>${job.match_score}%</td>
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

    goToView("resumeView");

    showStatusMessage("Job link added. Click \"Extract Job Description\" to continue.");
}

export function renderSectorPicker() {
    const container = document.getElementById("jobSectorPicker");

    if (!state.jobSectors.length) {
        container.innerHTML = "";
        return;
    }

    container.innerHTML = state.jobSectors.map((sector) => `
        <label class="sector-option">
            <input type="checkbox" value="${sector}" checked onchange="toggleJobSector('${sector}')">
            ${sector}
        </label>
    `).join("");
}

export function toggleJobSector(sector) {
    if (state.selectedJobSectors.includes(sector)) {
        state.selectedJobSectors = state.selectedJobSectors.filter((s) => s !== sector);
    } else {
        state.selectedJobSectors.push(sector);
    }
}

export async function suggestSectors() {
    const button = document.getElementById("suggestSectorsButton");
    const spinner = document.getElementById("suggestSectorsSpinner");

    try {
        if (!state.resumeJson) {
            showStatusMessage("Upload your resume first.");
            return;
        }

        button.disabled = true;
        spinner.style.display = "inline-block";

        const strategy = await apiJson("/generate-search-queries", {
            method: "POST",
            body: JSON.stringify({ resume_json: state.resumeJson }),
        });

        state.jobSectors = strategy.sectors || [];
        state.selectedJobSectors = [...state.jobSectors];

        renderSectorPicker();

        showStatusMessage("Sectors suggested from your resume. Uncheck any you want to exclude.");

    } catch (error) {
        console.log(error);
        showStatusMessage("Could not suggest sectors right now.");
    } finally {
        button.disabled = false;
        spinner.style.display = "none";
    }
}

export async function findJobs() {
    try {
        if (!state.resumeJson) {
            showStatusMessage("Upload your resume first.");
            return;
        }

        document.getElementById("promisingJobsList").innerHTML = `
            <tr>
                <td colspan="7">
                    <div class="loading-state">
                        <div class="loading-spinner"></div>
                        Searching for matching jobs...
                    </div>
                </td>
            </tr>
        `;

        const country = document.getElementById("jobCountrySelect").value;
        const location = document.getElementById("jobLocationInput").value.trim();

        const jobTypes = ["jobTypeFullTime", "jobTypePartTime", "jobTypeContract", "jobTypePermanent"]
            .map(id => document.getElementById(id))
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        const salaryMin = document.getElementById("jobSalaryMin").value;
        const salaryMax = document.getElementById("jobSalaryMax").value;
        const maxDaysOld = document.getElementById("jobMaxDaysOld").value;
        const distance = document.getElementById("jobDistance").value;

        const data = await apiJson("/search-jobs", {
            method: "POST",
            body: JSON.stringify({
                resume_json: state.resumeJson,
                country,
                location: location || null,
                selected_sectors: state.jobSectors.length ? state.selectedJobSectors : null,
                job_types: jobTypes.length ? jobTypes : null,
                salary_min: salaryMin ? Number(salaryMin) : null,
                salary_max: salaryMax ? Number(salaryMax) : null,
                max_days_old: maxDaysOld ? Number(maxDaysOld) : null,
                distance: distance ? Number(distance) : null,
            }),
        });

        if (!data.jobs) {
            console.log(data);

            document.getElementById("promisingJobsList").innerHTML = `
                <tr>
                    <td colspan="7">
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
                <td colspan="7">
                    Something went wrong while searching for jobs.
                </td>
            </tr>
        `;
    }
}
