let mediaRecorder = null;
let recordedChunks = [];
let mediaStream = null;

export async function startRecording() {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });

    recordedChunks = [];
    mediaRecorder = new MediaRecorder(mediaStream);

    mediaRecorder.addEventListener("dataavailable", (event) => {
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    });

    mediaRecorder.start();
}

export function stopRecording() {
    return new Promise((resolve) => {
        mediaRecorder.addEventListener("stop", () => {
            const blob = new Blob(recordedChunks, { type: "audio/webm" });

            mediaStream.getTracks().forEach((track) => track.stop());
            mediaStream = null;

            resolve(blob);
        });

        mediaRecorder.stop();
    });
}
