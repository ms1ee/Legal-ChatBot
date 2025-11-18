import base64
import json
import os
from pathlib import Path

import requests
import streamlit as st
from PIL import Image

from css import THEME_CHOICES, get_theme_css

BACKEND_URL = os.getenv("LEXAI_BACKEND_URL", "http://127.0.0.1:9000")
COLUMN_HEIGHT = 780
CHAT_LOG_HEIGHT = 520
FRONTEND_DIR = Path(__file__).resolve().parent
LOGO_PATH = FRONTEND_DIR.parent / "LexAI_Logo.png"
LOGO_DATA_URI = ""
PAGE_ICON = "⚖️"

if LOGO_PATH.exists():
    logo_bytes = LOGO_PATH.read_bytes()
    LOGO_DATA_URI = base64.b64encode(logo_bytes).decode("utf-8")
    try:
        with Image.open(LOGO_PATH) as raw_logo:
            PAGE_ICON = raw_logo.copy()
    except Exception:
        PAGE_ICON = "⚖️"


def _preview_text(*candidates):
    for text in candidates:
        if not text:
            continue
        snippet = text.strip().split()[0][:60]
        if snippet:
            return snippet
    return "New chat"


def _derive_title_from_record(record):
    if not record:
        return "New chat"
    title = record.get("title")
    messages = record.get("messages") or []
    if title and title != "New chat":
        return _preview_text(title)
    assistant_texts = [
        msg.get("content")
        for msg in messages
        if msg.get("role") == "assistant"
    ]
    preview = _preview_text(*assistant_texts)
    if preview != "New chat":
        return preview
    return _preview_text(title)

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "disclaimer" not in st.session_state:
        st.session_state.disclaimer = ""
    if "session_meta" not in st.session_state:
        st.session_state.session_meta = {
            "model": "대기 중",
            "generation_config": {},
            "usage": {},
        }
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "conversation_list" not in st.session_state:
        st.session_state.conversation_list = []
    if "conversations_loaded" not in st.session_state:
        st.session_state.conversations_loaded = False
    if "rename_target" not in st.session_state:
        st.session_state.rename_target = None
    if "conversation_search" not in st.session_state:
        st.session_state.conversation_search = ""
    if "ui_theme" not in st.session_state:
        st.session_state.ui_theme = "light"
    if "current_title" not in st.session_state:
        st.session_state.current_title = "New chat"
    if "title_cache" not in st.session_state:
        st.session_state.title_cache = {}

def reset_conversation():
    st.session_state.messages = []
    st.session_state.session_meta = {
        "model": "대기 중",
        "generation_config": {},
        "usage": {},
    }
    st.session_state.disclaimer = ""
    st.session_state.conversation_id = None
    st.session_state.current_title = "New chat"


def _theme_label_from_key(theme_key):
    for label, key in THEME_CHOICES.items():
        if key == theme_key:
            return label
    return next(iter(THEME_CHOICES.keys()))


def render_sidebar_header():
    logo_html = ""
    if LOGO_DATA_URI:
        logo_html = (
            f'<img src="data:image/png;base64,{LOGO_DATA_URI}" '
            'alt="LexAI logo" class="sidebar-logo"/>'
        )
    st.markdown(
        f"""
        <div class="sidebar-header">
            {logo_html}
            <div>
                <div class="sidebar-headline">LexAI</div>
                <div class="sidebar-subtitle">한국 법률 전문가</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_theme_controls():
    st.caption("색상 모드")
    labels = list(THEME_CHOICES.keys())
    current_label = _theme_label_from_key(st.session_state.ui_theme)
    default_index = labels.index(current_label)
    selection = st.radio(
        "색상 테마",
        options=labels,
        index=default_index,
        horizontal=True,
        label_visibility="collapsed",
        key="__theme_selector",
    )
    st.session_state.ui_theme = THEME_CHOICES.get(selection, "light")
    return st.session_state.ui_theme


def render_message(message):
    is_assistant = message["role"] == "assistant"
    avatar = "🤖" if is_assistant else "🧑‍⚖️"
    bubble_class = "chat-assistant" if is_assistant else "chat-user"
    alignment = "flex-start" if is_assistant else "flex-end"
    st.markdown(
        f"""
        <div style="display: flex; justify-content:{alignment};">
            <div class="chat-bubble {bubble_class}">
                <span class="avatar">{avatar}</span>
                <span class="message-text">{message["content"]}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_conversation(conversation_placeholder):
    conversation_placeholder.empty()
    hero_prompt = None
    with conversation_placeholder.container():
        st.markdown('<div class="conversation-shell">', unsafe_allow_html=True)
        st.markdown(
            '<div class="conversation-body scrollable">', unsafe_allow_html=True
        )
        chat_started = any(msg["role"] == "user" for msg in st.session_state.messages)
        if chat_started:
            for message in st.session_state.messages:
                render_message(message)
        else:
            st.markdown(
                """
                <div class="hero-state">
                    <h1 class="hero-greeting">안녕하세요</h1>
                    <p>법률 관련 질문을 입력해 보세요. LexAI가 해결해드릴게요.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            hero_prompt = render_hero_input()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    return chat_started, hero_prompt


def render_session_panel():
    meta = st.session_state.session_meta
    cfg = meta.get("generation_config") or {}
    usage = meta.get("usage") or {}
    st.markdown(
        f"""
        <div class="session-card">
            <small>MODEL</small>
            <div class="session-headline">{meta.get("model", "알 수 없음")}</div>
            <div class="session-metrics">
                <div>
                    <strong>{cfg.get("temperature", "-")}</strong>
                    <span>temperature</span>
                </div>
                <div>
                    <strong>{cfg.get("top_p", "-")}</strong>
                    <span>top&nbsp;p</span>
                </div>
                <div>
                    <strong>{cfg.get("max_new_tokens", "-")}</strong>
                    <span>max&nbsp;tokens</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="session-card">
            <small>USAGE</small>
            <div class="session-usage">
                <div>프롬프트 <strong>{usage.get("prompt_tokens", "–")}</strong></div>
                <div>응답 <strong>{usage.get("completion_tokens", "–")}</strong></div>
                <div>총합 <strong>{usage.get("total_tokens", "–")}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero_input():
    st.session_state.setdefault("hero_prompt_input", "")
    if st.session_state.pop("hero_prompt_reset_pending", False):
        st.session_state.hero_prompt_input = ""

    st.markdown('<div class="hero-input-wrapper">', unsafe_allow_html=True)
    hero_prompt = st.text_area(
        "LexAI에게 물어보기",
        key="hero_prompt_input",
        placeholder="법률 관련 질문을 입력하세요.",
        label_visibility="collapsed",
        height=120,
    )
    send = st.button(
        "질문 보내기",
        key="hero_submit",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    if send:
        text = (hero_prompt or "").strip()
        if text:
            st.session_state.hero_prompt_reset_pending = True
            return text
    return None


def stream_backend(prompt, history, conversation_id):
    payload = {
        "conversation_id": conversation_id,
        "message": prompt,
        "history": history,
    }
    with requests.post(
        f"{BACKEND_URL}/chat/stream",
        json=payload,
        stream=True,
        timeout=None,
    ) as response:
        response.raise_for_status()
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            if not raw_line.startswith("data:"):
                continue
            data = raw_line[5:].strip()
            if not data:
                continue
            if data == "[DONE]":
                break
            try:
                event = json.loads(data.lstrip())
            except json.JSONDecodeError:
                continue
            yield event


def handle_user_prompt(prompt, conversation_placeholder):
    prompt = (prompt or "").strip()
    if not prompt:
        return

    history_payload = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ]
    current_conversation_id = st.session_state.conversation_id

    st.session_state.messages.append({"role": "user", "content": prompt})
    assistant_message = {
        "role": "assistant",
        "content": "Lexi가 응답 중입니다…",
    }
    st.session_state.messages.append(assistant_message)
    render_conversation(conversation_placeholder)

    final_received = False
    stream_failed = False
    stream_notice_active = True
    try:
        for event in stream_backend(
            prompt, history_payload, current_conversation_id
        ):
            event_type = event.get("type")
            if event_type == "start":
                st.session_state.session_meta = {
                    "model": event.get("model", "미상"),
                    "generation_config": event.get("generation_config", {}),
                    "usage": {},
                }
            elif event_type == "delta":
                text = event.get("text")
                if text is not None:
                    assistant_message["content"] = text or assistant_message["content"]
                    if stream_notice_active:
                        stream_notice_active = False
                    render_conversation(conversation_placeholder)
            elif event_type == "final":
                assistant_message["content"] = event.get(
                    "reply", assistant_message["content"]
                )
                st.session_state.disclaimer = event.get(
                    "disclaimer", st.session_state.disclaimer
                )
                st.session_state.session_meta["model"] = event.get(
                    "model",
                    st.session_state.session_meta.get("model", "미상"),
                )
                st.session_state.session_meta["generation_config"] = event.get(
                    "generation_config",
                    st.session_state.session_meta.get("generation_config", {}),
                )
                st.session_state.session_meta["usage"] = event.get("usage", {}) or {}
                st.session_state.conversation_id = event.get(
                    "conversation_id",
                    st.session_state.get("conversation_id"),
                )
                preview_title = _preview_text(
                    event.get("reply"), assistant_message["content"]
                )
                st.session_state.current_title = preview_title
                if st.session_state.conversation_id:
                    st.session_state.title_cache[
                        st.session_state.conversation_id
                    ] = preview_title
                final_received = True
                render_conversation(conversation_placeholder)
                break
            elif event_type == "error":
                st.error(event.get("message", "스트리밍 중 오류가 발생했습니다."))
                stream_failed = True
                break
    except requests.RequestException as exc:
        stream_failed = True
        st.error(f"Backend error: {exc}")
    finally:
        if stream_failed or not final_received:
            st.session_state.messages.pop()
        else:
            refresh_conversation_list()


def refresh_conversation_list():
    try:
        response = requests.get(f"{BACKEND_URL}/conversations", timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return
    st.session_state.conversation_list = response.json()
    st.session_state.conversations_loaded = True
    for conv in st.session_state.conversation_list:
        conv_id = conv.get("id")
        if not conv_id:
            continue
        title = conv.get("title")
        if title and title != "New chat":
            st.session_state.title_cache[conv_id] = title
            continue
        if conv_id in st.session_state.title_cache:
            continue
        try:
            preview_response = requests.get(
                f"{BACKEND_URL}/conversations/{conv_id}", timeout=10
            )
            preview_response.raise_for_status()
        except requests.RequestException:
            continue
        preview_record = preview_response.json()
        st.session_state.title_cache[conv_id] = _derive_title_from_record(
            preview_record
        )


def load_conversation(conversation_id):
    try:
        response = requests.get(
            f"{BACKEND_URL}/conversations/{conversation_id}", timeout=10 
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"대화 로드 실패: {exc}")
        return
    record = response.json()
    st.session_state.messages = record.get("messages") or []
    st.session_state.conversation_id = record.get("id")
    st.session_state.disclaimer = st.session_state.disclaimer or ""
    preview_title = _derive_title_from_record(record)
    st.session_state.current_title = preview_title
    if record.get("id"):
        st.session_state.title_cache[record["id"]] = preview_title


def start_rename(conversation):
    st.session_state.rename_target = conversation["id"]
    key = f"rename-input-{conversation['id']}"
    st.session_state[key] = conversation.get("title") or "New chat"
    st.rerun()


def cancel_rename():
    st.session_state.rename_target = None
    st.rerun()


def rename_conversation(conversation_id, new_title):
    try:
        response = requests.post(
            f"{BACKEND_URL}/conversations/{conversation_id}/title",
            json={"title": new_title},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"제목 변경 실패: {exc}")
        return
    st.session_state.rename_target = None
    st.session_state.title_cache[conversation_id] = new_title
    if st.session_state.conversation_id == conversation_id:
        st.session_state.current_title = new_title or st.session_state.current_title
    refresh_conversation_list()
    st.rerun()


def main():
    st.set_page_config(
        page_title="LexAI",
        layout="wide",
        page_icon=PAGE_ICON,
    )

    theme_style_slot = st.empty()
    init_state()

    if not st.session_state.conversations_loaded:
        refresh_conversation_list()

    st.markdown('<div class="lexi-columns-marker"></div>', unsafe_allow_html=True)
    left_col, right_col = st.columns([0.26, 0.74], gap="medium")

    with left_col:
        render_sidebar_header()
        # current_theme = render_theme_controls()
        current_theme = st.session_state.ui_theme
        theme_style_slot.markdown(
            get_theme_css(current_theme), unsafe_allow_html=True
        )
        if st.button(
            "새 채팅", key="left-new-chat", use_container_width=True, type="secondary"
        ):
            reset_conversation()
            st.rerun()
        st.markdown('<div class="sidebar-title">세션 정보</div>', unsafe_allow_html=True)
        render_session_panel()
        st.markdown('<div class="sidebar-title">채팅 로그</div>', unsafe_allow_html=True)
        st.text_input(
            "검색",
            key="conversation_search",
            placeholder="대화목록 검색하기",
            label_visibility="collapsed",
        )
        log_container = st.container(height=CHAT_LOG_HEIGHT, border=False)
        with log_container:
            st.markdown('<div class="chat-log-list scrollable">', unsafe_allow_html=True)
            conversations = st.session_state.conversation_list
            search_term = (
                st.session_state.get("conversation_search") or ""
            ).strip().lower()

            def _conv_title(conv_record):
                return (
                    st.session_state.title_cache.get(conv_record.get("id"))
                    or conv_record.get("title")
                    or "New chat"
                )

            if search_term:
                conversations = [
                    conv
                    for conv in conversations
                    if search_term in _conv_title(conv).lower()
                ]
            if not conversations:
                empty_message = (
                    "검색 결과가 없습니다."
                    if st.session_state.conversation_list
                    else "저장된 대화가 없습니다."
                )
                st.caption(empty_message)
            else:
                for conv in conversations:
                    title = _conv_title(conv)
                    is_active = conv.get("id") == st.session_state.conversation_id
                    row = st.container()
                    row.markdown(
                        f'<div class="chat-log-entry{" active" if is_active else ""}">',
                        unsafe_allow_html=True,
                    )
                    cols = row.columns([0.82, 0.18], gap="small")
                    if cols[0].button(
                        title, key=f"conv-{conv['id']}", use_container_width=True
                    ):
                        load_conversation(conv["id"])
                        refresh_conversation_list()
                        st.rerun()
                    if cols[1].button(
                        "⋯",
                        key=f"rename-btn-{conv['id']}",
                        use_container_width=True,
                    ):
                        start_rename(conv)
                    if st.session_state.rename_target == conv["id"]:
                        input_key = f"rename-input-{conv['id']}"
                        new_title = row.text_input("새 제목", key=input_key)
                        save_col, cancel_col = row.columns(2)
                        if save_col.button(
                            "저장",
                            key=f"rename-save-{conv['id']}",
                            use_container_width=True,
                        ):
                            rename_conversation(conv["id"], new_title)
                        if cancel_col.button(
                            "취소",
                            key=f"rename-cancel-{conv['id']}",
                            use_container_width=True,
                        ):
                            cancel_rename()
                    row.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    current_title = st.session_state.get("current_title", "New chat")

    with right_col:
        with st.container(height=COLUMN_HEIGHT, border=False):
            st.markdown(
                f'<div class="workspace-title">{current_title}</div>',
                unsafe_allow_html=True,
            )
            conversation_placeholder = st.empty()
            chat_started, hero_prompt = render_conversation(conversation_placeholder)
            prompt = hero_prompt if not chat_started else st.chat_input(
                "LexAI에게 물어보기"
            )
            if prompt:
                handle_user_prompt(prompt, conversation_placeholder)
                st.rerun()


if __name__ == "__main__":
    main()
