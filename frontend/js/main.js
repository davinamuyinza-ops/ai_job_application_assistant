import { extractJobFromUrl, analyzeJob } from "./analysis.js";
import { celebrate, rippleOnClick, spotlightFollow } from "./animation.js";
import { getSession, isSupabaseConfigured, onAuthStateChange, signIn, signOut, signUp } from "./auth.js";
import { deleteApplication, loadApplicationsFromBackend, openApplicationDocuments, renderSavedApplications, saveApplication, updateApplicationStatus } from "./applications.js";
import { copyCoverLetter, generateCoverLetter, generateResume } from "./documents.js";
import { findJobs, renderPromisingJobs, suggestSectors, toggleJobSector, usePromisingJob } from "./jobs.js";
import { initMotivationRecorder } from "./motivationRecorder.js";
import { confirmParsedResume, discardParsedResume, loadMasterResume, parseResumePdf, uploadResumeJsonFile } from "./resume.js";
import { initResumeEditorBridge, sendAuthTokenToEditor } from "./resumeEditor.js";
import { state } from "./state.js";
import { goToView, showAppShell, showAuthScreen, showStatusMessage } from "./ui.js";

// Table rows for applications/jobs are rendered as HTML strings with inline
// onclick handlers, so those two functions need to be reachable globally.
window.deleteApplication = deleteApplication;
window.updateApplicationStatus = updateApplicationStatus;
window.usePromisingJob = usePromisingJob;
window.toggleJobSector = toggleJobSector;
window.openApplicationDocuments = openApplicationDocuments;

function wireRippleEffect() {
    document.addEventListener("click", (event) => {
        const button = event.target.closest("button");

        if (button) {
            rippleOnClick({ currentTarget: button, clientX: event.clientX, clientY: event.clientY });
        }
    });
}

function wireNav() {
    document.querySelectorAll("[data-view]").forEach(button => {
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

function renderActionResultsSummary(results) {
    const container = document.getElementById("actionResultsSummary");

    container.innerHTML = "";

    results.forEach((result, index) => {
        const line = document.createElement("div");
        line.className = `action-result ${result.ok ? "success" : "error"}`;
        line.textContent = result.message;
        line.style.animationDelay = `${index * 120}ms`;
        container.appendChild(line);
    });
}

async function runSelectedActions() {
    const doResume = document.getElementById("checkGenerateResume").checked;
    const doCoverLetter = document.getElementById("checkGenerateCoverLetter").checked;
    const doSave = document.getElementById("checkSaveApplication").checked;

    if (!doResume && !doCoverLetter && !doSave) {
        showStatusMessage("Select at least one action first.");
        return;
    }

    const continueButton = document.getElementById("runSelectedActionsButton");
    continueButton.disabled = true;

    // Resume and cover letter each render their own progress/result inline in
    // their Documents card, so we jump there right away and let the user
    // watch both generate side by side, rather than waiting on Analysis.
    if (doResume || doCoverLetter) {
        goToView("documentsView");

        const [resumeResult, coverLetterResult] = await Promise.all([
            doResume ? generateResume() : Promise.resolve(null),
            doCoverLetter ? generateCoverLetter() : Promise.resolve(null),
        ]);

        if (resumeResult?.ok || coverLetterResult?.ok) {
            celebrate(document.querySelector(".documents-grid"));
        }

        // Saving waits for generation so the finished documents are stored
        // with the application instead of being lost on refresh.
        const saveResult = doSave ? await saveApplication() : null;

        if (saveResult) {
            showStatusMessage(saveResult.message);
        }
    } else {
        const saveResult = await saveApplication();

        if (saveResult.ok) {
            celebrate(document.querySelector(".sidebar-nav"));
            goToView("applicationsView");
        } else {
            renderActionResultsSummary([saveResult]);
        }
    }

    continueButton.disabled = false;
}

function wireActionButtons() {
    document.getElementById("extractButton").addEventListener("click", extractJobFromUrl);
    document.getElementById("analyzeButton").addEventListener("click", analyzeJob);
    document.getElementById("runSelectedActionsButton").addEventListener("click", runSelectedActions);
    document.getElementById("copyCoverLetterButton").addEventListener("click", copyCoverLetter);
    document.getElementById("suggestSectorsButton").addEventListener("click", suggestSectors);
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
    wireRippleEffect();

    const heroCard = document.querySelector(".hero-card");

    if (heroCard) {
        spotlightFollow(heroCard);
    }

    wireNav();
    wireAuthForms();
    wireResumeUploads();
    wireActionButtons();
    initMotivationRecorder();
    initResumeEditorBridge();

    if (!isSupabaseConfigured()) {
        document.getElementById("authError").textContent =
            "Supabase is not configured yet - set SUPABASE_URL and SUPABASE_ANON_KEY in frontend/js/config.js.";
        showAuthScreen();
        return;
    }

    onAuthStateChange((session) => {
        if (session) {
            // Forwards Supabase's hourly token refresh to the embedded editor.
            sendAuthTokenToEditor();
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
