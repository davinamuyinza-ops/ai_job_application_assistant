import { staggerReveal } from "./animation.js";
import { state } from "./state.js";

export function showStatusMessage(message) {
    const status = document.getElementById("statusMessage");

    status.textContent = message;
    status.style.display = "block";

    setTimeout(() => {
        status.style.display = "none";
    }, 3000);
}

function measureStepperTrack(stepper) {
    const badges = stepper.querySelectorAll(".step-badge");

    if (badges.length < 2) {
        return;
    }

    const containerRect = stepper.getBoundingClientRect();
    const firstBadgeRect = badges[0].getBoundingClientRect();
    const lastBadgeRect = badges[badges.length - 1].getBoundingClientRect();

    const startX = firstBadgeRect.left + firstBadgeRect.width / 2 - containerRect.left;
    const endX = lastBadgeRect.left + lastBadgeRect.width / 2 - containerRect.left;

    stepper.style.setProperty("--track-start", `${startX}px`);
    stepper.style.setProperty("--track-end", `${endX}px`);
}

export function refreshGating() {
    const hasResume = Boolean(state.resumeJson);
    const hasAnalysis = Boolean(state.jobAnalysis);
    const hasTailoredResume = Boolean(state.tailoredResume);
    const hasCoverLetter = Boolean(state.coverLetter);

    const activeViewId = document.querySelector(".view-section.active-view")?.id;

    const analysisStep = document.querySelector('.step[data-view="analysisView"]');
    const documentsStep = document.querySelector('.step[data-view="documentsView"]');
    const resumeEditorNavButton = document.querySelector('.nav-button[data-view="resumeEditorView"]');

    if (analysisStep) {
        analysisStep.disabled = !hasResume;
    }

    if (documentsStep) {
        documentsStep.disabled = !hasAnalysis;
    }

    if (resumeEditorNavButton) {
        resumeEditorNavButton.disabled = !hasTailoredResume;
    }

    document.querySelectorAll(".step").forEach(step => {
        step.classList.remove("active");
        step.classList.remove("completed");
    });

    const resumeJobStep = document.querySelector('.step[data-view="resumeView"]');

    if (resumeJobStep && hasAnalysis) {
        resumeJobStep.classList.add("completed");
    }

    if (analysisStep && hasAnalysis) {
        analysisStep.classList.add("completed");
    }

    if (documentsStep && (hasTailoredResume || hasCoverLetter)) {
        documentsStep.classList.add("completed");
    }

    const activeStep = document.querySelector(`.step[data-view="${activeViewId}"]`);

    if (activeStep) {
        activeStep.classList.add("active");
    }

    const stepperTrack = document.getElementById("pipelineStepper");

    if (stepperTrack) {
        measureStepperTrack(stepperTrack);

        const completedCount = [resumeJobStep, analysisStep].filter(
            step => step?.classList.contains("completed"),
        ).length;

        stepperTrack.style.setProperty("--stepper-progress", completedCount / 2);
    }
}

export function showView(viewId, buttonElement = null) {
    document.querySelectorAll(".view-section").forEach(view => {
        view.classList.remove("active-view");
    });

    const targetView = document.getElementById(viewId);

    if (targetView) {
        targetView.classList.add("active-view");
        staggerReveal(targetView, ".card, .document-card, .overview-card, .stat-card");
    }

    // The Resume Editor is a design tool that benefits from as much screen
    // real estate as possible, so it gets a dedicated fullscreen-ish mode
    // (sidebar/header tucked away) that no other view uses.
    document.getElementById("appShell")?.classList.toggle("editor-fullscreen", viewId === "resumeEditorView");

    document.querySelectorAll(".nav-button, .step").forEach(button => {
        button.classList.remove("active");
    });

    if (buttonElement) {
        buttonElement.classList.add("active");
    }

    refreshGating();
}

export function goToView(viewId) {
    showView(viewId, document.querySelector(`[data-view="${viewId}"]`));
}

export function showAuthScreen() {
    document.getElementById("authView").style.display = "flex";
    document.getElementById("appShell").style.display = "none";
}

export function showAppShell() {
    document.getElementById("authView").style.display = "none";
    document.getElementById("appShell").style.display = "flex";
}
