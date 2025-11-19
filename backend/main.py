import asyncio
import json
import logging
from queue import Queue
from threading import Thread

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
    if request.model_variant == "compare":
        raise HTTPException(
            status_code=400, detail="비교 모드는 스트리밍 API에서만 지원됩니다."
        )
    try:
        (reply, usage), model_label = await generate_reply(
            request.history, request.message, request.model_variant
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
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
        model=model_label,
        generation_config=GenerationConfig(
            max_new_tokens=config.MAX_NEW_TOKENS,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
        ),
        usage=usage,
    )


def _single_stream_generator(request: ChatRequest, history_dicts):
    def event_stream():
        try:
            model_label, generator = stream_reply_chunks(
                request.history, request.message, request.model_variant
            )
        except ValueError as exc:
            yield _sse_payload({"type": "error", "message": str(exc)})
            yield "data: [DONE]\n\n"
            return

        final_reply = ""
        last_usage = None

        yield _sse_payload(
            {
                "type": "start",
                "mode": "single",
                "model": model_label,
                "models": [
                    {"variant": request.model_variant, "model": model_label}
                ],
                "generation_config": _generation_config_payload(),
            }
        )

        try:
            for chunk in generator:
                final_reply = chunk.text
                if chunk.usage is not None:
                    last_usage = chunk.usage.model_dump()

                yield _sse_payload(
                    {
                        "type": "delta",
                        "mode": "single",
                        "variant": request.model_variant,
                        "model": model_label,
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
                    "mode": "single",
                    "conversation_id": record["id"],
                    "title": record.get("title", "New chat"),
                    "reply": final_reply,
                    "disclaimer": config.DISCLAIMER,
                    "model": model_label,
                    "models": [
                        {"variant": request.model_variant, "model": model_label}
                    ],
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

    return event_stream()


def _compare_stream_generator(request: ChatRequest, history_dicts):
    def event_stream():
        variant_pairs = []
        try:
            for variant in config.COMPARISON_VARIANTS:
                model_label, generator = stream_reply_chunks(
                    request.history, request.message, variant
                )
                variant_pairs.append((variant, model_label, generator))
        except ValueError as exc:
            yield _sse_payload({"type": "error", "message": str(exc)})
            yield "data: [DONE]\n\n"
            return

        if not variant_pairs:
            yield _sse_payload(
                {"type": "error", "message": "비교할 모델이 설정되지 않았습니다."}
            )
            yield "data: [DONE]\n\n"
            return

        models_payload = [
            {"variant": variant, "model": model_label}
            for variant, model_label, _ in variant_pairs
        ]

        yield _sse_payload(
            {
                "type": "start",
                "mode": "compare",
                "models": models_payload,
                "generation_config": _generation_config_payload(),
            }
        )

        event_queue: Queue = Queue()
        final_map: dict[str, dict] = {}

        def _pump(variant, model_label, generator):
            final_reply = ""
            last_usage = None
            try:
                for chunk in generator:
                    final_reply = chunk.text
                    if chunk.usage is not None:
                        last_usage = chunk.usage.model_dump()
                    event_queue.put(
                        (
                            "delta",
                            variant,
                            model_label,
                            {
                                "text": chunk.text,
                                "delta": chunk.delta,
                                "finished": chunk.finished,
                                "usage": last_usage,
                            },
                        )
                    )
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "Failed to stream response for variant %s", variant
                )
                event_queue.put(("error", variant, str(exc)))
                return

            event_queue.put(
                ("done", variant, model_label, final_reply, last_usage)
            )

        threads = [
            Thread(target=_pump, args=pair, daemon=True) for pair in variant_pairs
        ]
        for thread in threads:
            thread.start()

        completed = 0
        total = len(variant_pairs)
        encountered_error = False

        while completed < total:
            item = event_queue.get()
            kind = item[0]
            if kind == "delta":
                _, variant, model_label, payload = item
                yield _sse_payload(
                    {
                        "type": "delta",
                        "mode": "compare",
                        "variant": variant,
                        "model": model_label,
                        **payload,
                    }
                )
            elif kind == "error":
                _, variant, message = item
                encountered_error = True
                yield _sse_payload(
                    {
                        "type": "error",
                        "variant": variant,
                        "message": message,
                    }
                )
                break
            elif kind == "done":
                _, variant, model_label, final_reply, last_usage = item
                final_map[variant] = {
                    "model": model_label,
                    "reply": final_reply,
                    "usage": last_usage,
                }
                completed += 1

        for thread in threads:
            thread.join(timeout=0.1)

        if not encountered_error and final_map:
            reply_sections = []
            for variant in config.COMPARISON_VARIANTS:
                data = final_map.get(variant)
                if not data:
                    continue
                reply_sections.append(
                    f"[{data['model']}]\n{data['reply']}".strip()
                )
            combined_reply = "\n\n".join(reply_sections).strip()

            record = save_conversation(
                request.conversation_id,
                request.message,
                combined_reply,
                history_dicts,
            )

            yield _sse_payload(
                {
                    "type": "final",
                    "mode": "compare",
                    "conversation_id": record["id"],
                    "title": record.get("title", "New chat"),
                    "reply": combined_reply,
                    "disclaimer": config.DISCLAIMER,
                    "models": models_payload,
                    "variants": final_map,
                    "generation_config": _generation_config_payload(),
                }
            )

        yield "data: [DONE]\n\n"

    return event_stream()


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    history_dicts = [msg.dict() for msg in request.history]
    if request.model_variant == "compare":
        generator = _compare_stream_generator(request, history_dicts)
    else:
        generator = _single_stream_generator(request, history_dicts)

    return StreamingResponse(
        iterate_in_threadpool(generator),
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
