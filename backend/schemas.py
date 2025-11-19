from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, constr, field_validator

from . import config


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str
    content: constr(strip_whitespace=True, min_length=1)

    @field_validator("role")
    @classmethod
    def _validate_role(cls, value):
        allowed = {"system", "user", "assistant"}
        if value not in allowed:
            raise ValueError(f"role must be one of {', '.join(allowed)}")
        return value


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: str | None = None
    message: constr(strip_whitespace=True, min_length=1)
    history: list[ChatMessage] = Field(
        default_factory=list,
        description="Chronological chat history excluding the new user message.",
    )
    model_variant: Literal["baseline", "finetuned", "compare"] = Field(
        default=config.DEFAULT_MODEL_VARIANT
    )


class UsageReport(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class GenerationConfig(BaseModel):
    max_new_tokens: int
    temperature: float
    top_p: float


class ChatResponse(BaseModel):
    conversation_id: str
    title: str
    reply: str
    disclaimer: str
    model: str
    generation_config: GenerationConfig
    usage: UsageReport | None = None
