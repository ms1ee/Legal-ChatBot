import os

import requests
import streamlit as st

from css import CUSTOM_CSS

BACKEND_URL = os.getenv("LEXAI_BACKEND_URL", "http://127.0.0.1:9000")
COLUMN_HEIGHT = 800

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

def reset_conversation():
    st.session_state.messages = []
    st.session_state.session_meta = {
        "model": "대기 중",
        "generation_config": {},
        "usage": {},
    }
    st.session_state.disclaimer = ""
    st.session_state.conversation_id = None


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
    with conversation_placeholder.container():
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
        st.markdown("</div>", unsafe_allow_html=True)


def render_session_panel():
    meta = st.session_state.session_meta
    cfg = meta.get("generation_config") or {}
    usage = meta.get("usage") or {}
    st.markdown(
        f"""
        <div class="session-card">
            <div class="session-card-title">모델 정보</div>
            <div><strong>모델</strong>: {meta.get("model", "알 수 없음")}</div>
            <div class="session-meta">
                temperature {cfg.get("temperature", "-")}<br/>
                top_p {cfg.get("top_p", "-")}<br/>
                max_tokens {cfg.get("max_new_tokens", "-")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="session-card">
            <div class="session-card-title">토큰 사용량</div>
            <div>프롬프트: {usage.get("prompt_tokens", "–")} tokens</div>
            <div>응답: {usage.get("completion_tokens", "–")} tokens</div>
            <div>총합: {usage.get("total_tokens", "–")} tokens</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def call_backend(prompt):
    history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages[:-1]
    ]
    payload = {
        "conversation_id": st.session_state.conversation_id,
        "message": prompt,
        "history": history,
    }
    response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=90)
    response.raise_for_status()
    return response.json()


def refresh_conversation_list():
    try:
        response = requests.get(f"{BACKEND_URL}/conversations", timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return
    st.session_state.conversation_list = response.json()
    st.session_state.conversations_loaded = True


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
    refresh_conversation_list()
    st.rerun()


def main():
    st.set_page_config(
        page_title="LexAI",
        layout="wide",
        page_icon="⚖️",
    )

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    init_state()

    if not st.session_state.conversations_loaded:
        refresh_conversation_list()

    st.markdown('<h1 class="main-header">LexAI</h1>', unsafe_allow_html=True)
    st.markdown('<div class="lexi-columns-marker"></div>', unsafe_allow_html=True)
    left_col, right_col = st.columns([0.2, 0.8], gap="small")

    with left_col:
        with st.container(height=COLUMN_HEIGHT, border=False):
            if st.button(
                "새 채팅", key="left-new-chat", use_container_width=True, type="primary"
            ):
                reset_conversation()
                st.rerun()
            st.markdown(
                '<div class="sidebar-title">세션 정보</div>', unsafe_allow_html=True
            )
            render_session_panel()
            st.markdown(
                '<div class="sidebar-title">채팅 로그</div>', unsafe_allow_html=True
            )
            st.markdown('<div class="sidebar-search">', unsafe_allow_html=True)
            st.text_input(
                "검색",
                key="conversation_search",
                placeholder="대화목록 검색하기",
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="chat-log-list scrollable">', unsafe_allow_html=True)
            conversations = st.session_state.conversation_list
            search_term = (
                st.session_state.get("conversation_search") or ""
            ).strip().lower()
            if search_term:
                conversations = [
                    conv
                    for conv in conversations
                    if search_term in (conv.get("title") or "New chat").lower()
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
                    title = conv.get("title") or "New chat"
                    is_active = conv.get("id") == st.session_state.conversation_id
                    row = st.container()
                    row.markdown(
                        f'<div class="chat-log-entry{" active" if is_active else ""}">',
                        unsafe_allow_html=True,
                    )
                    cols = row.columns([0.85, 0.15], gap="small")
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

    current_title = "New chat"
    if st.session_state.conversation_id:
        for conv in st.session_state.conversation_list:
            if conv["id"] == st.session_state.conversation_id:
                current_title = conv.get("title") or current_title
                break

    with right_col:
        with st.container(height=COLUMN_HEIGHT, border=False):
            header_cols = st.columns([0.9, 0.1])
            header_cols[0].markdown(
                f"""
                <div>
                    <div class="workspace-eyebrow">LexAI</div>
                    <div class="workspace-title">{current_title}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if header_cols[1].button(
                "새 채팅", key="right-new-chat", use_container_width=True
            ):
                reset_conversation()
                st.rerun()
            conversation_placeholder = st.empty()
            render_conversation(conversation_placeholder)
            if prompt := st.chat_input("LexAI에게 물어보기"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                render_conversation(conversation_placeholder)
                with st.spinner("Contacting LexAI…"):
                    try:
                        backend_response = call_backend(prompt)
                    except requests.RequestException as exc:
                        st.error(f"Backend error: {exc}")
                    else:
                        st.session_state.disclaimer = backend_response.get(
                            "disclaimer", ""
                        )
                        st.session_state.session_meta = {
                            "model": backend_response.get("model", "미상"),
                            "generation_config": backend_response.get(
                                "generation_config", {}
                            ),
                            "usage": backend_response.get("usage", {}),
                        }
                        st.session_state.messages.append(
                            {"role": "assistant", "content": backend_response["reply"]}
                        )
                        st.session_state.conversation_id = backend_response.get(
                            "conversation_id",
                            st.session_state.get("conversation_id"),
                        )
                        refresh_conversation_list()
                st.rerun()

    if st.session_state.disclaimer:
        st.info(st.session_state.disclaimer)


if __name__ == "__main__":
    main()
