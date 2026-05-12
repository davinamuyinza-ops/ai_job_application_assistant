let storedResumeJson = null;
let storedJobDescription = "";
let storedJobAnalysis = null;
let storedTailoredResume = null;
let storedCoverLetter = null;

async function analyzeJob() {

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
    document.getElementById("results").textContent =
        JSON.stringify(data, null, 2);

}

async function generateResume() {

    const requestBody = {
        job_description: storedJobDescription,
        resume_json: storedResumeJson,
        job_analysis: storedJobAnalysis
    };

    console.log(requestBody);

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
        JSON.stringify(data, null, 2);
}

async function generateCoverLetter() {

    const requestBody = {
        job_description: storedJobDescription,
        resume_json: storedResumeJson,
        job_analysis: storedJobAnalysis
    };

    console.log(requestBody);

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
        JSON.stringify(data, null, 2);
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

    URL.revokeObjectURL(url);
}

function downloadCoverLetter() {

    const text =
        JSON.stringify(
            storedCoverLetter,
            null,
            2
        );

    const blob = new Blob(
        [text],
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
        "cover_letter.json";

    link.click();

    URL.revokeObjectURL(url);
}