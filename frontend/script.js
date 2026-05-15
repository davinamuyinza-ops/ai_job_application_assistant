let storedResumeJson = null;
let storedJobDescription = "";
let storedJobAnalysis = null;
let storedTailoredResume = null;
let storedCoverLetter = null;
let savedApplications = [];
let promisingJobs = [];

const API_BASE_URL = "http://127.0.0.1:8000";

function showStatusMessage(message) {

    const status =
        document.getElementById("statusMessage");

    status.textContent = message;

    status.style.display = "block";

    setTimeout(() => {
        status.style.display = "none";
    }, 3000);
}

function setStep(stepNumber) {

    const steps =
        document.querySelectorAll(".step");

    steps.forEach(step => {
        step.classList.remove("active");
        step.classList.remove("completed");
    });

    for (let i = 0; i < stepNumber - 1; i++) {
        steps[i].classList.add("completed");
    }

    steps[stepNumber - 1].classList.add("active");
}

async function analyzeJob() {
    
    try {
        document.getElementById("analyzeButton").disabled = true;
        
        const jobDescription =
            document.getElementById("jobDescription").value;

        
        storedJobDescription = jobDescription;

        if (!storedResumeJson) {
            document.getElementById("analysisResults").textContent =
                "Please upload your resume first.";

            return;
        }

        const requestBody = {
            job_description: jobDescription,
            resume_json: storedResumeJson
        };

        console.log(requestBody);

        document.getElementById("analysisResults").textContent =
        "Analyzing job description...";

        const response = await fetch(`${API_BASE_URL}/analyze-job`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        storedJobAnalysis = data;
        
        // JSON.stringify(data, null, 2) formats the JSON data with indentation for better readability
        document.getElementById("analysisResults").textContent =
        `
            Match Score: ${data.match_analysis.match_score}

            Application Priority: ${data.decision.priority}

            Should Apply: ${data.decision.should_apply}

            Confidence: ${data.decision.confidence}%

            Main Reason:${data.decision.reason}
        `;

        setStep(2);
    
    } catch (error) {
        console.log(error);

        document.getElementById("analysisResults").textContent =
            "Something went wrong while analyzing the job.";
    }finally {
        document.getElementById("analyzeButton").disabled = false;
    }

}

async function generateResume() {

    try {
        document.getElementById("resumeButton").disabled = true;

        const requestBody = {
            job_description: storedJobDescription,
            resume_json: storedResumeJson,
            job_analysis: storedJobAnalysis
        };

        console.log(requestBody);

        document.getElementById("resumeResults").textContent =
        "Generating tailored resume...";

        const response = await fetch(
            `${API_BASE_URL}/tailor-resume`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestBody)
            }
        );

        const data = await response.json();
        storedTailoredResume = data.tailored_resume_json;

        console.log(data);

        document.getElementById("resumeResults").textContent =
            "Tailored resume generated successfully. Ready for download.";

        setStep(3);

    } catch (error) {
        console.log(error);

        document.getElementById("resumeResults").textContent =
            "Something went wrong while generating the tailored resume.";
    }finally {
        document.getElementById("resumeButton").disabled = false;
    }
}

async function generateCoverLetter() {

    try {
        document.getElementById("coverLetterButton").disabled = true;
        const requestBody = {
            job_description: storedJobDescription,
            resume_json: storedResumeJson,
            job_analysis: storedJobAnalysis
        };

        console.log(requestBody);

        document.getElementById("coverLetterResults").textContent =
        "Generating cover letter...";

        const response = await fetch(
            `${API_BASE_URL}/generate-cover-letter`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestBody)
            }
        );

        const data = await response.json();
        storedCoverLetter = data;

        console.log(data);

        document.getElementById("coverLetterResults").textContent =
            data.cover_letter;

        setStep(4);

    } catch (error) {
        console.log(error);

        document.getElementById("coverLetterResults").textContent =
            "Something went wrong while generating the cover letter.";
    }finally {
        document.getElementById("coverLetterButton").disabled = false;
    }
}

function downloadResumeJson() {

    const jsonString =
        JSON.stringify(
            storedTailoredResume,
            null,
            2
        );

    const blob = new Blob(
        [jsonString],
        {
            type: "application/json"
        }
    );

    const url =
        URL.createObjectURL(blob);

    const link =
        document.createElement("a");

    link.href = url;

    link.download =
        "tailored_resume.json";

    link.click();

    showStatusMessage("Tailored resume downloaded successfully.");

    URL.revokeObjectURL(url);
}

function copyCoverLetter() {
    const coverLetterText = storedCoverLetter.cover_letter;

    navigator.clipboard.writeText(coverLetterText);

    showStatusMessage("Cover letter copied successfully.");
}

async function extractJobFromUrl() {
    try {
        document.getElementById("extractButton").disabled = true;

        const jobUrl = document.getElementById("jobLink").value;

        document.getElementById("jobDescription").value =
            "Extracting job description from URL...";

        const requestBody = {
            job_url: jobUrl
        };

        const response = await fetch(`${API_BASE_URL}/extract-job`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        document.getElementById("jobDescription").value =
            data.job_text;

        showStatusMessage("Job description extracted successfully.");

    } catch (error) {
        console.log(error);

        document.getElementById("jobDescription").value =
            "";

        showStatusMessage("Could not extract job description from this URL.");

    } finally {
        document.getElementById("extractButton").disabled = false;
    }
}

async function saveApplication() {

    const applicationData = {
        id: Date.now(),

        company:
            storedJobAnalysis.core_fields.company,

        role:
            storedJobAnalysis.core_fields.job_title,

        matchScore:
            storedJobAnalysis.match_analysis.match_score,

        priority:
            storedJobAnalysis.decision.priority,

        shouldApply:
            String(storedJobAnalysis.decision.should_apply),

        status: "Saved",

        date:
            new Date().toLocaleDateString(),

        jobLink:
            document.getElementById("jobLink").value
    };

    savedApplications.push(applicationData);

    localStorage.setItem(
        "savedApplications",
        JSON.stringify(savedApplications)
    );

    await fetch(`${API_BASE_URL}/save-application`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            company: applicationData.company,
            role: applicationData.role,
            match_score: applicationData.matchScore,
            priority: applicationData.priority,
            should_apply: applicationData.shouldApply,
            status: applicationData.status,
            application_date: applicationData.date,
            job_link: applicationData.jobLink
        })
    });

    showStatusMessage(
        "Application saved successfully."
    );

    renderSavedApplications();
    updateDashboardStats();
}

function renderSavedApplications() {

    const list =
        document.getElementById("savedApplicationsList");

    const selectedFilter =
        document.getElementById("statusFilter").value;

    const sortOption =
    document.getElementById("sortOption").value;

    list.innerHTML = "";

    let filteredApplications =
    [...savedApplications];

    if (sortOption === "highestScore") {

        filteredApplications.sort(
            (a, b) => b.matchScore - a.matchScore
        );

    } else if (sortOption === "lowestScore") {

        filteredApplications.sort(
            (a, b) => a.matchScore - b.matchScore
        );

    } else {

        filteredApplications.reverse();
    }

    filteredApplications.forEach((application, index) => {

        if (
            selectedFilter !== "All" &&
            application.status !== selectedFilter
        ) {
            return;
        }

        const row =
            document.createElement("tr");

        row.innerHTML = `
            <td>${application.company}</td>
            <td>${application.role}</td>
            <td>${application.matchScore}</td>
            <td>${application.priority}</td>
            <td>${application.shouldApply}</td>

            <td>
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
                <button onclick="deleteApplication(${application.id})">
                    Delete
                </button>
            </td>
        `;

        list.appendChild(row);
    });
}

async function updateApplicationStatus(id, newStatus) {

    await fetch(
        `${API_BASE_URL}/applications/${id}/status?status=${newStatus}`,
        {
            method: "PUT"
        }
    );

    const application =
        savedApplications.find(
            app => app.id === id
        );

    if (application) {
        application.status = newStatus;
    }

    localStorage.setItem(
        "savedApplications",
        JSON.stringify(savedApplications)
    );

    renderSavedApplications();

    updateDashboardStats();
}

const storedApplications =
    localStorage.getItem("savedApplications");

if (storedApplications) {
    savedApplications =
        JSON.parse(storedApplications);

    renderSavedApplications();
    updateDashboardStats();
}

async function deleteApplication(id) {

    await fetch(`${API_BASE_URL}/applications/${id}`, {
        method: "DELETE"
    });

    savedApplications =
        savedApplications.filter(
            app => app.id !== id
        );

    localStorage.setItem(
        "savedApplications",
        JSON.stringify(savedApplications)
    );

    renderSavedApplications();

    updateDashboardStats();

    showStatusMessage(
        "Application deleted."
    );
}

function updateDashboardStats() {

    document.getElementById("totalCount").textContent =
        savedApplications.length;

    document.getElementById("appliedCount").textContent =
        savedApplications.filter(
            app => app.status === "Applied"
        ).length;

    document.getElementById("interviewCount").textContent =
        savedApplications.filter(
            app => app.status === "Interview"
        ).length;

    document.getElementById("offerCount").textContent =
        savedApplications.filter(
            app => app.status === "Offer"
        ).length;
}

const storedResume =
    localStorage.getItem("savedResume");

if (storedResume) {

    storedResumeJson =
        JSON.parse(storedResume);

    showStatusMessage(
        "Saved resume loaded successfully."
    );
}

function renderPromisingJobs() {

    const list =
        document.getElementById("promisingJobsList");

    list.innerHTML = "";

    promisingJobs.forEach((job, index) => {

        const row =
            document.createElement("tr");

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

function usePromisingJob(index) {

    const selectedJob =
        promisingJobs[index];

    document.getElementById("jobLink").value =
        selectedJob.link;

    showStatusMessage(
        "Job link added successfully."
    );
}

async function findJobs() {
    try {
        if (!storedResumeJson) {
            document.getElementById("promisingJobsList").innerHTML =
                `
                <tr>
                    <td colspan="6">
                        Please upload your resume first.
                    </td>
                </tr>
                `;

            return;
        }

        document.getElementById("promisingJobsList").innerHTML =
            `
            <tr>
                <td colspan="6">
                    Searching for matching jobs...
                </td>
            </tr>
            `;

        const requestBody = {
            resume_json: storedResumeJson
        };

        const response = await fetch(`${API_BASE_URL}/search-jobs`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (!data.jobs) {
            console.log(data);

            document.getElementById("promisingJobsList").innerHTML =
                `
                <tr>
                    <td colspan="6">
                        Backend did not return job results.
                    </td>
                </tr>
                `;

            return;
        }

promisingJobs = data.jobs;

        renderPromisingJobs();

        showStatusMessage("Matching jobs found successfully.");

    } catch (error) {
        console.log(error);

        document.getElementById("promisingJobsList").innerHTML =
            `
            <tr>
                <td colspan="6">
                    Something went wrong while searching for jobs.
                </td>
            </tr>
            `;
    }
}

document.getElementById("resumeUpload").addEventListener("change", async function () {
    const file = this.files[0];

    if (!file) {
        return;
    }

    const fileText = await file.text();

    const resumeJson = JSON.parse(fileText);

    storedResumeJson = resumeJson;

    localStorage.setItem(
        "savedResume",
        JSON.stringify(resumeJson)
    );

    showStatusMessage("Resume uploaded and saved successfully.");
});

async function loadApplicationsFromBackend() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/applications`
        );

        const data = await response.json();

        savedApplications = data.map(app => ({
            id: app.id,
            company: app.company,
            role: app.role,
            matchScore: app.match_score,
            priority: app.priority,
            shouldApply: app.should_apply,
            status: app.status,
            date: app.application_date,
            jobLink: app.job_link
        }));

        renderSavedApplications();
        updateDashboardStats();

    } catch (error) {

        console.log(error);

        showStatusMessage(
            "Failed to load applications from database."
        );
    }
}

loadApplicationsFromBackend();