import { extractJobFromUrl, analyzeJob } from "./analysis.js";
import { getSession, isSupabaseConfigured, onAuthStateChange, signIn, signOut, signUp } from "./auth.js";
import { deleteApplication, loadApplicationsFromBackend, renderSavedApplications, saveApplication, updateApplicationStatus } from "./applications.js";
import { copyCoverLetter, downloadResumeJson, generateCoverLetter, generateResume } from "./documents.js";
import { findJobs, renderPromisingJobs, usePromisingJob } from "./jobs.js";
import { confirmParsedResume, discardParsedResume, loadMasterResume, parseResumePdf, uploadResumeJsonFile } from "./resume.js";
import { state } from "./state.js";
import { goToView, showAppShell, showAuthScreen, showStatusMessage } from "./ui.js";

// Table rows for applications/jobs are rendered as HTML strings with inline
// onclick handlers, so those two functions need to be reachable globally.
window.deleteApplication = deleteApplication;
window.updateApplicationStatus = updateApplicationStatus;
window.usePromisingJob = usePromisingJob;

function wireNav() {
    document.querySelectorAll(".nav-button[data-view]").forEach(button => {
        button.addEventListener("click", () => goToView(button.dataset.view));
    });

    document.querySelectorAll("[data-goto]").forEach(button => {
        button.addEventListener("click", () => goToView(button.dataset.goto));
    });
}

function wireAuthForms() {
    const signInTab = document.getElementById("showSignInTab");
    const signUpTab = document.getElementById("showSignUpTab");
    const signInForm = document.getElementById("signInForm");
    const signUpForm = document.getElementById("signUpForm");
    const authError = document.getElementById("authError");

    signInTab.addEventListener("click", () => {
        signInForm.style.display = "flex";
        signUpForm.style.display = "none";
        signInTab.classList.add("active");
        signUpTab.classList.remove("active");
        authError.textContent = "";
    });

    signUpTab.addEventListener("click", () => {
        signUpForm.style.display = "flex";
        signInForm.style.display = "none";
        signUpTab.classList.add("active");
        signInTab.classList.remove("active");
        authError.textContent = "";
    });

    signInForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        authError.textContent = "";

        try {
            await signIn(
                document.getElementById("signInEmail").value,
                document.getElementById("signInPassword").value,
            );
        } catch (error) {
            authError.textContent = error.message || "Could not sign in.";
        }
    });

    signUpForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        authError.textContent = "";

        try {
            await signUp(
                document.getElementById("signUpEmail").value,
                document.getElementById("signUpPassword").value,
            );

            authError.textContent = "Account created. Check your email to confirm, then sign in.";
        } catch (error) {
            authError.textContent = error.message || "Could not sign up.";
        }
    });

    document.getElementById("signOutButton").addEventListener("click", async () => {
        await signOut();
    });
}

function renderMasterResumeStatus() {
    const el = document.getElementById("masterResumeStatus");

    el.textContent = state.resumeJson
        ? "Master resume on file - ready to use for job analysis."
        : "No master resume saved yet.";
}

function wireResumeUploads() {
    document.getElementById("resumeUploadJson").addEventListener("change", async function () {
        const file = this.files[0];

        if (!file) {
            return;
        }

        try {
            await uploadResumeJsonFile(file);
            renderMasterResumeStatus();
        } catch (error) {
            console.log(error);
            showStatusMessage("Could not read that JSON file.");
        }

        this.value = "";
    });

    document.getElementById("resumeUploadPdf").addEventListener("change", async function () {
        const file = this.files[0];

        if (!file) {
            return;
        }

        try {
            showStatusMessage("Extracting resume content from PDF...");

            const parsed = await parseResumePdf(file);

            document.getElementById("resumeReviewContent").textContent = JSON.stringify(parsed, null, 2);
            document.getElementById("resumeReviewPanel").style.display = "block";
        } catch (error) {
            console.log(error);
            showStatusMessage(error.message || "Could not parse that PDF.");
        }

        this.value = "";
    });

    document.getElementById("confirmSaveResumeButton").addEventListener("click", async () => {
        await confirmParsedResume();
        document.getElementById("resumeReviewPanel").style.display = "none";
        renderMasterResumeStatus();
    });

    document.getElementById("discardParsedResumeButton").addEventListener("click", () => {
        discardParsedResume();
        document.getElementById("resumeReviewPanel").style.display = "none";
    });
}

function wireActionButtons() {
    document.getElementById("extractButton").addEventListener("click", extractJobFromUrl);
    document.getElementById("analyzeButton").addEventListener("click", analyzeJob);
    document.getElementById("resumeButton").addEventListener("click", generateResume);
    document.getElementById("coverLetterButton").addEventListener("click", generateCoverLetter);
    document.getElementById("saveApplicationButton").addEventListener("click", saveApplication);
    document.getElementById("downloadResumeButton").addEventListener("click", downloadResumeJson);
    document.getElementById("copyCoverLetterButton").addEventListener("click", copyCoverLetter);
    document.getElementById("findJobsButton").addEventListener("click", findJobs);
    document.getElementById("statusFilter").addEventListener("change", renderSavedApplications);
    document.getElementById("sortOption").addEventListener("change", renderSavedApplications);
}

async function initApp() {
    await loadMasterResume();
    renderMasterResumeStatus();

    await loadApplicationsFromBackend();
    renderPromisingJobs();

    goToView("dashboardView");
}

async function bootstrap() {
    wireNav();
    wireAuthForms();
    wireResumeUploads();
    wireActionButtons();

    if (!isSupabaseConfigured()) {
        document.getElementById("authError").textContent =
            "Supabase is not configured yet - set SUPABASE_URL and SUPABASE_ANON_KEY in frontend/js/config.js.";
        showAuthScreen();
        return;
    }

    onAuthStateChange((session) => {
        if (session) {
            showAppShell();
            initApp();
        } else {
            showAuthScreen();
        }
    });

    const session = await getSession();

    if (session) {
        showAppShell();
        await initApp();
    } else {
        showAuthScreen();
    }
}

bootstrap();
