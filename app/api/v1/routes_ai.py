from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api import deps
from app.core.config import settings
from app.models.user import User
from app.schemas.ai import (
    AIImprovementRequest,
    AIImprovementResponse,
    TranscriptionResponse,
)
from app.services import ai as ai_service

router = APIRouter()


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    *,
    file: UploadFile = File(..., description="Audio file to transcribe"),
    language: str | None = Form(None, description="Optional language hint (e.g. 'ru')"),
    current_user: User = Depends(deps.get_current_user),
) -> TranscriptionResponse:
    """
    Transcribe an audio file using the local Whisper service.
    """
    text = await ai_service.transcribe_audio(file, language)
    return TranscriptionResponse(text=text, provider="whisper", language=language)


@router.post("/improve", response_model=AIImprovementResponse)
async def improve_text(
    payload: AIImprovementRequest,
    current_user: User = Depends(deps.get_current_user),
) -> AIImprovementResponse:
    """
    Improve a text snippet using the local LLM (LLaMA via OpenAI-compatible API).
    """
    improved = await ai_service.improve_text(
        prompt=payload.prompt,
        text=payload.text,
        model_override=payload.model,
    )
    model_used = payload.model or settings.LLM_MODEL
    return AIImprovementResponse(text=improved, model=model_used, provider="llama")
