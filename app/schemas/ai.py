from pydantic import BaseModel, Field


class TranscriptionResponse(BaseModel):
    text: str = Field(..., description="Transcript text")
    provider: str = Field(default="whisper", description="Transcription provider used")
    language: str | None = Field(default=None, description="Language detected or requested")


class AIImprovementRequest(BaseModel):
    text: str = Field(..., description="Original text to improve")
    prompt: str = Field(..., description="Prompt describing the improvement to apply")
    model: str | None = Field(default=None, description="LLM model override")


class AIImprovementResponse(BaseModel):
    text: str = Field(..., description="Improved text produced by the LLM")
    model: str = Field(..., description="Model that was used to generate the response")
    provider: str = Field(default="llama", description="LLM provider")
