const SpeechRecognitionImpl = window.SpeechRecognition || window.webkitSpeechRecognition;

export function isLiveCaptionSupported() {
    return Boolean(SpeechRecognitionImpl);
}

let recognition = null;

export function startLiveCaption(onUpdate) {
    if (!isLiveCaptionSupported()) {
        return;
    }

    recognition = new SpeechRecognitionImpl();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.addEventListener("result", (event) => {
        let text = "";

        for (let i = 0; i < event.results.length; i++) {
            text += event.results[i][0].transcript + " ";
        }

        onUpdate(text.trim());
    });

    recognition.addEventListener("error", () => {
        // Live preview is best-effort only - the real transcript comes from
        // the backend, so a recognition error here is silently ignored.
    });

    recognition.start();
}

export function stopLiveCaption() {
    if (recognition) {
        recognition.stop();
        recognition = null;
    }
}
