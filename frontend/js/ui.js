export function showStatusMessage(message) {
    const status = document.getElementById("statusMessage");

    status.textContent = message;
    status.style.display = "block";

    setTimeout(() => {
        status.style.display = "none";
    }, 3000);
}

export function setStep(stepNumber) {
    const steps = document.querySelectorAll(".step");

    if (!steps.length) {
        return;
    }

    steps.forEach(step => {
        step.classList.remove("active");
        step.classList.remove("completed");
    });

    for (let i = 0; i < stepNumber - 1; i++) {
        if (steps[i]) {
            steps[i].classList.add("completed");
        }
    }

    if (steps[stepNumber - 1]) {
        steps[stepNumber - 1].classList.add("active");
    }
}

export function showView(viewId, buttonElement = null) {
    document.querySelectorAll(".view-section").forEach(view => {
        view.classList.remove("active-view");
    });

    const targetView = document.getElementById(viewId);

    if (targetView) {
        targetView.classList.add("active-view");
    }

    document.querySelectorAll(".nav-button").forEach(button => {
        button.classList.remove("active");
    });

    if (buttonElement) {
        buttonElement.classList.add("active");
    }
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
