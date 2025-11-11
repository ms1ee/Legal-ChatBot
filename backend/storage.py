import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[1] / "chat_logs"
LOG_DIR.mkdir(exist_ok=True)


def _conversation_path(conversation_id):
    return LOG_DIR / f"{conversation_id}.json"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def list_conversations():
    conversations = []
    for path in sorted(LOG_DIR.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            conversations.append(
                {
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "updated_at": data.get("updated_at"),
                    "created_at": data.get("created_at"),
                }
            )
        except json.JSONDecodeError:
            continue
    conversations.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    return conversations


def load_conversation(conversation_id):
    path = _conversation_path(conversation_id)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _default_title(message):
    if not message:
        return "New chat"
    snippet = message.strip().splitlines()[0][:40]
    return snippet or "New chat"


def save_conversation(conversation_id, user_message, assistant_message, history):
    if conversation_id is None:
        conversation_id = uuid.uuid4().hex
        title = _default_title(user_message)
        record = {
            "id": conversation_id,
            "title": title,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "messages": history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ],
        }
    else:
        record = load_conversation(conversation_id) or {
            "id": conversation_id,
            "title": _default_title(user_message),
            "created_at": _now_iso(),
            "messages": history,
        }
        if not record.get("title"):
            record["title"] = _default_title(user_message)
        record.setdefault("messages", history)
        record["messages"] = history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ]
        record["updated_at"] = _now_iso()

    path = _conversation_path(conversation_id)
    with path.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return record


def update_conversation_title(conversation_id, title):
    if not title:
        raise ValueError("title must not be empty")
    record = load_conversation(conversation_id)
    if record is None:
        return None
    record["title"] = title
    record["updated_at"] = _now_iso()
    path = _conversation_path(conversation_id)
    with path.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return record
