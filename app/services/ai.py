import logging
import re

import httpx
from fastapi import HTTPException, UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)


def _merge_prompt(prompt: str, text: str) -> str:
    """
    Combine prompt and user text, ensuring the text is embedded even
    if the prompt does not contain a placeholder.
    """
    prompt = prompt.strip()
    text = text.strip()

    if not prompt:
        return text

    placeholder_pattern = re.compile(r"{text}", re.IGNORECASE)
    if placeholder_pattern.search(prompt):
        return placeholder_pattern.sub(f"\"{text}\"", prompt)

    return f"{prompt}\n\n\"{text}\""


async def transcribe_audio(file: UploadFile, language: str | None = None) -> str:
    """Send audio to the Whisper service and return transcription text."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty")

    data: dict[str, str] = {}
    if language:
        data["language"] = language

    files = {
        "file": (
            file.filename or "audio.m4a",
            content,
            file.content_type or "audio/m4a",
        )
    }

    try:
        async with httpx.AsyncClient(timeout=settings.WHISPER_API_TIMEOUT) as client:
            response = await client.post(settings.WHISPER_API_URL, data=data, files=files)
    except httpx.RequestError as exc:
        logger.exception("Whisper request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Whisper service is not reachable at the moment",
        ) from exc

    if response.status_code >= 400:
        logger.error(
            "Whisper service responded with %s: %s",
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=502,
            detail="Failed to transcribe audio with Whisper service",
        )

    payload = response.json()
    text = payload.get("text") or payload.get("transcription") or payload.get("result")
    if isinstance(text, dict):
        text = text.get("text") or text.get("transcription")

    if not text:
        logger.error("Whisper response missing text: %s", payload)
        raise HTTPException(
            status_code=502,
            detail="Transcription service returned an empty response",
        )

    return str(text).strip()


async def improve_text(prompt: str, text: str, model_override: str | None = None) -> str:
    """Call the local LLM (OpenAI compatible) to improve user text."""
    model = model_override or settings.LLM_MODEL
    user_prompt = _merge_prompt(prompt, text)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": settings.LLM_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": settings.LLM_TEMPERATURE,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
            response = await client.post(settings.LLM_API_URL, json=payload)
    except httpx.RequestError as exc:
        logger.exception("LLM request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="LLM service is not reachable at the moment",
        ) from exc

    if response.status_code >= 400:
        logger.error(
            "LLM service responded with %s: %s",
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=502,
            detail="LLM service failed to generate text",
        )

    data = response.json()
    result_text = None

    if isinstance(data, dict):
        choices = data.get("choices") or []
        if choices:
            choice0 = choices[0]
            message = choice0.get("message") if isinstance(choice0, dict) else None
            if isinstance(message, dict):
                result_text = message.get("content")
            if not result_text and isinstance(choice0, dict):
                result_text = choice0.get("text")

        if not result_text:
            result_text = data.get("response") or data.get("text")

    if not result_text:
        logger.error("LLM response missing text: %s", data)
        raise HTTPException(
            status_code=502,
            detail="LLM returned an empty response",
        )

    return str(result_text).strip()
