from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.core.security import get_current_user
from app.services.transcription import transcribe_audio

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/transcribe")
async def transcribe(audio: UploadFile):
    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="No audio data received.")

    try:
        transcript = transcribe_audio(audio_bytes, audio.filename or "recording.webm")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"error": "Transcription failed", "message": str(exc)},
        )

    return {"transcript": transcript}
