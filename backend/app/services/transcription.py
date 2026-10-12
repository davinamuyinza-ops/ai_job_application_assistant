from app.services.ai_client import client


def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    audio_file = (filename, audio_bytes)

    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
    )

    return response.text
