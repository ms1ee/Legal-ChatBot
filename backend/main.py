import asyncio
import json
import logging

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import iterate_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from . import config
from .schemas import ChatRequest, ChatResponse, GenerationConfig
from .services.vllm_client import (
    generate_reply,
    stream_reply_chunks,
    warm_up_local_engine,
)
from .storage import (
    list_conversations,
    load_conversation,
    save_conversation,
    update_conversation_title,
)

logger = logging.getLogger(__name__)


def _generation_config_payload():
    return {
        "max_new_tokens": config.MAX_NEW_TOKENS,
        "temperature": config.TEMPERATURE,
        "top_p": config.TOP_P,
    }


def _sse_payload(data):
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

app = FastAPI(
    title="Lexi Legal Chatbot API",
    version="0.1.0",
    description="FastAPI backend that proxies requests to a vLLM served model.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Warm up local vLLM before serving requests."""

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, warm_up_local_engine)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    history_dicts = [msg.dict() for msg in request.history]
    try:
        reply, usage = await generate_reply(request.history, request.message)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to get response from vLLM.")
        raise HTTPException(status_code=502, detail=str(exc))

    record = save_conversation(
        request.conversation_id,
        request.message,
        reply,
        history_dicts,
    )

    return ChatResponse(
        conversation_id=record["id"],
        title=record.get("title", "New chat"),
        reply=reply,
        disclaimer=config.DISCLAIMER,
        model=config.MODEL_DISPLAY_NAME,
        generation_config=GenerationConfig(
            max_new_tokens=config.MAX_NEW_TOKENS,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
        ),
        usage=usage,
    )


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    history_dicts = [msg.dict() for msg in request.history]

    def event_stream():
        final_reply = ""
        last_usage = None

        yield _sse_payload(
            {
                "type": "start",
                "model": config.MODEL_DISPLAY_NAME,
                "generation_config": _generation_config_payload(),
            }
        )

        try:
            for chunk in stream_reply_chunks(request.history, request.message):
                final_reply = chunk.text
                if chunk.usage is not None:
                    last_usage = chunk.usage.model_dump()

                yield _sse_payload(
                    {
                        "type": "delta",
                        "text": chunk.text,
                        "delta": chunk.delta,
                        "finished": chunk.finished,
                        "usage": last_usage,
                    }
                )

            record = save_conversation(
                request.conversation_id,
                request.message,
                final_reply,
                history_dicts,
            )

            yield _sse_payload(
                {
                    "type": "final",
                    "conversation_id": record["id"],
                    "title": record.get("title", "New chat"),
                    "reply": final_reply,
                    "disclaimer": config.DISCLAIMER,
                    "model": config.MODEL_DISPLAY_NAME,
                    "generation_config": _generation_config_payload(),
                    "usage": last_usage,
                }
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to stream response from vLLM.")
            yield _sse_payload(
                {
                    "type": "error",
                    "message": str(exc),
                }
            )
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        iterate_in_threadpool(event_stream()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/conversations")
async def get_conversations():
    return list_conversations()


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    record = load_conversation(conversation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return record


@app.post("/conversations/{conversation_id}/title")
async def rename_conversation(conversation_id: str, payload: dict):
    title = (payload or {}).get("title", "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title must not be empty.")
    record = update_conversation_title(conversation_id, title)
    if record is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"status": "ok", "conversation": record}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=9000, reload=True)
