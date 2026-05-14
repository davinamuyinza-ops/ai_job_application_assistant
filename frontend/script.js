let storedResumeJson = null;
let storedJobDescription = "";
let storedJobAnalysis = null;
let storedTailoredResume = null;
let storedCoverLetter = null;
let savedApplications = [];

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

        const fileInput =
            document.getElementById("resumeUpload");

        const file =
            fileInput.files[0];

        const fileText =
            await file.text();

        const resumeJson =
            JSON.parse(fileText);

        storedResumeJson = resumeJson;
        storedJobDescription = jobDescription;

        const requestBody = {
            job_description: jobDescription,
            resume_json: resumeJson
        };

        console.log(requestBody);

        document.getElementById("analysisResults").textContent =
        "Analyzing job description...";

        const response = await fetch("http://127.0.0.1:8000/analyze-job", {
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
            "http://127.0.0.1:8000/tailor-resume",
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
            "http://127.0.0.1:8000/generate-cover-letter",
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

        const response = await fetch("http://127.0.0.1:8000/extract-job", {
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

function saveApplication() {

    const applicationData = {
        company:
            storedJobAnalysis.core_fields.company,

        role:
            storedJobAnalysis.core_fields.job_title,

        matchScore:
            storedJobAnalysis.match_analysis.match_score,

        priority:
            storedJobAnalysis.decision.priority,

        shouldApply:
            storedJobAnalysis.decision.should_apply,

        date:
            new Date().toLocaleDateString()
    };

    savedApplications.push(applicationData);

    localStorage.setItem(
        "savedApplications",
        JSON.stringify(savedApplications)
    );

    console.log(savedApplications);

    showStatusMessage(
        "Application saved successfully."
    );

    renderSavedApplications();
}

function renderSavedApplications() {
    const list =
        document.getElementById("savedApplicationsList");

    list.innerHTML = "";

    savedApplications.forEach(application => {
        const item =
            document.createElement("div");

        item.className = "saved-application";

        item.innerHTML = `
            <strong>${application.company}</strong><br>
            ${application.role}<br>
            Match Score: ${application.matchScore}<br>
            Priority: ${application.priority}<br>
            Date: ${application.date}
        `;

        list.appendChild(item);
    });
}

const storedApplications =
    localStorage.getItem("savedApplications");

if (storedApplications) {
    savedApplications =
        JSON.parse(storedApplications);

    renderSavedApplications();
}