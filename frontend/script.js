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
    
    // JSON.stringify(data, null, 2) formats the JSON data with indentation for better readability
    document.getElementById("results").textContent =
        JSON.stringify(data, null, 2);

}