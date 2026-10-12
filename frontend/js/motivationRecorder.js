import { apiFetch } from "./api.js";
import { isLiveCaptionSupported, startLiveCaption, stopLiveCaption } from "./liveCaption.js";
import { startRecording, stopRecording } from "./recorder.js";
import { state } from "./state.js";

async function transcribeAudio(blob) {
    const formData = new FormData();
    formData.append("audio", blob, "recording.webm");

    const response = await apiFetch("/transcribe", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail?.detail?.message || "Transcription request failed.");
    }

    return response.json();
}

function describeMicError(error) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        return "This page can't reach the microphone API. It needs to be loaded over HTTPS or from localhost.";
    }

    switch (error.name) {
        case "NotAllowedError":
        case "PermissionDeniedError":
            return "Microphone access was blocked. Click the lock/camera icon in your browser's address bar and allow the microphone for this site, then try again.";
        case "NotFoundError":
        case "DevicesNotFoundError":
            return "No microphone was found. Check that one is connected and enabled in your system's sound settings.";
        case "NotReadableError":
        case "TrackStartError":
            return "The microphone couldn't be started - it may already be in use by another app (e.g. a video call).";
        case "SecurityError":
            return "Microphone access is blocked by this page's security context (needs HTTPS or localhost).";
        default:
            return `Could not access the microphone (${error.name || "unknown error"}: ${error.message || "no details"}).`;
    }
}

export function initMotivationRecorder() {
    const recordButton = document.getElementById("motivationRecordButton");
    const recordLabel = document.getElementById("motivationRecordLabel");
    const status = document.getElementById("motivationStatus");
    const liveCaptionArea = document.getElementById("motivationLiveCaptionArea");
    const liveCaptionText = document.getElementById("motivationLiveCaptionText");
    const transcribingStatus = document.getElementById("motivationTranscribingStatus");
    const transcriptText = document.getElementById("motivationTranscriptText");

    if (!recordButton) {
        return;
    }

    let isRecording = false;

    async function handleRecordToggleClick() {
        if (isRecording) {
            await stopAndTranscribe();
            return;
        }

        try {
            status.textContent = "";

            await startRecording();

            isRecording = true;
            recordButton.classList.add("recording");
            recordButton.setAttribute("aria-label", "Stop recording");
            recordLabel.textContent = "Recording... tap to stop";

            if (isLiveCaptionSupported()) {
                liveCaptionArea.style.display = "block";
                liveCaptionText.textContent = "";
                startLiveCaption((text) => {
                    liveCaptionText.textContent = text;
                });
            }
        } catch (error) {
            console.log(error);
            status.textContent = describeMicError(error);
        }
    }

    async function stopAndTranscribe() {
        isRecording = false;
        recordButton.classList.remove("recording");
        recordButton.setAttribute("aria-label", "Start recording");
        recordButton.disabled = true;
        recordLabel.textContent = "Tap to record";

        stopLiveCaption();
        liveCaptionArea.style.display = "none";

        const blob = await stopRecording();

        transcribingStatus.style.display = "block";

        try {
            const data = await transcribeAudio(blob);

            transcriptText.value = data.transcript;
            state.personalMotivation = data.transcript;
        } catch (error) {
            console.log(error);
            status.textContent = "Something went wrong while transcribing.";
        } finally {
            transcribingStatus.style.display = "none";
            recordButton.disabled = false;
        }
    }

    recordButton.addEventListener("click", handleRecordToggleClick);

    transcriptText.addEventListener("input", () => {
        state.personalMotivation = transcriptText.value;
    });
}
