import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("LEXI_BACKEND_URL", "http://127.0.0.1:9000")

st.set_page_config(
    page_title="법률 도우미 이도노",
    layout="wide",
    page_icon="⚖️",
)

CUSTOM_CSS = """
    <style>
    :root {
        --bg-color: #05070d;
        --panel-color: #0c111b;
        --panel-border: #141c2f;
        --text-primary: #edf1ff;
        --text-muted: #8c96b9;
        --accent: #4c7dff;
    }
    html, body {
        height: 100%;
        overflow: hidden;
    }
    body, .block-container {
        background: var(--bg-color);
        color: var(--text-primary);
        font-family: 'Pretendard', 'Inter', 'Noto Sans KR', sans-serif;
    }
    .block-container {
        padding: 1rem 1.5rem 1rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    div[data-testid="stAppViewContainer"] > .main {
        padding: 0;
        height: 100%;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    header[data-testid="stHeader"] {
        background: transparent;
    }
    .main-header {
        display: none;
    }
    .lexi-columns-marker {
        display: none;
    }
    .lexi-columns-marker + div[data-testid="stColumns"] {
        column-gap: 2rem;
        align-items: stretch;
        height: calc(100vh - 40px);
        flex: 1;
    }
    .lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"] {
        position: relative;
        height: 100%;
        min-height: 0;
        display: flex;
        flex-direction: column;
    }
    .lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"] > div {
        flex: 1;
        min-height: 0;
        display: flex;
        flex-direction: column;
    }
    .lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"] > div > div[data-testid="stVerticalBlock"] {
        flex: 1;
        min-height: 0;
        display: flex;
        flex-direction: column;
        scrollbar-color: #1c2234 transparent;
    }
    .lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"]:first-of-type > div[data-testid="stVerticalBlock"]:first-of-type {
        background: var(--panel-color);
        border: 1px solid var(--panel-border);
        border-radius: 24px;
        padding: 1.25rem;
        gap: 1rem;
        box-shadow: 0 30px 60px rgba(3, 5, 9, 0.65);
    }
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .sidebar-search input {
        background: #080c14;
        border: 1px solid #192136;
        color: var(--text-primary);
        border-radius: 18px;
    }
    .sidebar-search input::placeholder {
        color: var(--text-muted);
    }
    .session-card {
        background: linear-gradient(145deg, #11192d, #0c1323);
        border-radius: 18px;
        border: 1px solid #1d2540;
        padding: 1rem;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
        margin-bottom: 0.75rem;
    }
    .session-card-title {
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 0.35rem;
    }
    .session-meta {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-top: 0.35rem;
    }
    .chat-log-list {
        flex: 1;
        overflow-y: auto;
        padding-right: 0.2rem;
        display: flex;
        flex-direction: column;
        gap: 0;
    }
    .chat-log-list div[data-testid="stVerticalBlock"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    .chat-log-list div[data-testid="column"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    .chat-log-entry div[data-testid="stHorizontalBlock"] {
        align-items: stretch;
    }
    .chat-log-entry div[data-testid="column"] {
        display: flex;
    }
    .chat-log-entry div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
        flex: 1;
        display: flex;
    }
    .chat-log-entry div[data-testid="element-container"] {
        margin: 0 !important;
        padding: 0 !important;
        width: 100%;
        display: flex;
    }
    .chat-log-entry {
        width: 100%;
        margin: 0;
    }
    .chat-log-entry div[data-testid="stButton"] {
        width: 100%;
        margin: 0 !important;
        display: flex;
        flex: 1;
        align-items: stretch;
    }
    .chat-log-entry button {
        width: 100%;
        text-align: left;
        justify-content: center;
        flex-direction: column;
        margin: 0 !important;
        background: #0f1626;
        color: var(--text-primary);
        border: none;
        border-radius: 16px;
        padding: 0.45rem 0.8rem;
        font-weight: 500;
        min-height: 48px;
        display: flex;
        gap: 0.2rem;
        height: 100%;
        line-height: 1.4;
    }
    .chat-log-entry.active button {
        border-color: rgba(76, 125, 255, 0.6);
        background: rgba(76, 125, 255, 0.15);
    }
    .chat-log-entry button:hover {
        border-color: rgba(76, 125, 255, 0.45);
    }
    .chat-log-entry div[data-testid="column"]:nth-of-type(2) {
        display: flex;
    }
    .chat-log-entry div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"] {
        display: flex;
        flex: 1;
    }
    .chat-log-entry div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] {
        display: flex;
        flex: 1;
    }
    .chat-log-entry div[data-testid="column"]:nth-of-type(2) button {
        background: #0f1a2c;
        border: none;
        color: var(--text-muted);
        flex-direction: row;
        justify-content: center;
        align-items: center;
        padding: 0.38rem;
        min-width: 48px;
    }
    .lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"]:first-of-type {
        display: flex;
        flex-direction: column;
        padding: 2rem 2.25rem 1rem;
        background: radial-gradient(circle at top, rgba(76, 125, 255, 0.12), transparent 38%),
            #05070d;
        border-radius: 32px;
        border: 1px solid #0b1020;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.01);
    }
    .workspace-title {
        font-size: 1.85rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .workspace-eyebrow {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.4em;
        color: var(--text-muted);
    }
    .chat-bubble {
        border-radius: 22px;
        padding: 0.9rem 1.1rem;
        margin: 0.45rem 0;
        max-width: 92%;
        display: inline-flex;
        gap: 0.65rem;
        background: #0e1628;
        border: 1px solid #1b2238;
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.25);
    }
    .chat-assistant {
        background: linear-gradient(135deg, rgba(76, 125, 255, 0.15), rgba(9, 14, 27, 0.8));
        border-color: rgba(76, 125, 255, 0.3);
    }
    .chat-user {
        background: linear-gradient(135deg, rgba(250, 212, 117, 0.18), rgba(25, 23, 14, 0.9));
        border-color: rgba(250, 212, 117, 0.45);
    }
    .avatar {
        font-size: 1.6rem;
    }
    .message-text {
        flex: 1;
        line-height: 1.5;
    }
    .conversation-body {
        flex: 1;
        overflow-y: auto;
        padding-right: 0.5rem;
        padding-bottom: 1rem;
    }
    .hero-state {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        height: 100%;
        gap: 1rem;
        color: var(--text-muted);
    }
    .hero-greeting {
        font-size: 2.7rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3a7bff, #79a8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-name {
        color: #6ba0ff;
    }
    .scrollable::-webkit-scrollbar {
        width: 8px;
    }
    .scrollable::-webkit-scrollbar-thumb {
        background: #1c2234;
        border-radius: 10px;
    }
    .scrollable::-webkit-scrollbar-track {
        background: transparent;
    }
    div[data-testid="stChatInput"] {
        border-radius: 26px;
        border: 1px solid #131a2aed;
        background: #05070d;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
        margin-top: 0.5rem;
    }
    div[data-testid="stChatInput"] textarea {
        background: transparent;
        color: var(--text-primary);
        font-size: 1rem;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #69759c;
    }
    div[data-testid="stChatInput"] button {
        background: var(--accent);
        color: #fff;
        border-radius: 18px;
        border: none;
        box-shadow: 0 8px 20px rgba(76, 125, 255, 0.45);
    }
    .stButton button, .stTextInput input {
        transition: all 0.2s ease;
    }
    </style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

COLUMN_HEIGHT = 1600  # px height for column containers to enable native scroll


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "안녕하세요, 한국 법률 상담을 도와드리는 Lexi입니다. 필요하신 내용을 말씀해 주세요!",
            }
        ]
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


init_state()


def reset_conversation():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요, 한국 법률 상담을 도와드리는 Lexi입니다. 필요하신 내용을 말씀해 주세요!",
        }
    ]
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


def render_session_panel():
    meta = st.session_state.session_meta
    cfg = meta.get("generation_config") or {}
    usage = meta.get("usage") or {}
    st.markdown(
        f"""
        <div class="session-card">
            <div class="session-card-title">모델 정보</div>
            <div><strong>모델</strong>: {meta.get("model", "알 수 없음")}</div>
            <div class="session-meta">temperature {cfg.get("temperature", "-")}, top_p {cfg.get("top_p", "-")}, max_tokens {cfg.get("max_new_tokens", "-")}</div>
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
    st.session_state.messages = record.get("messages") or [
        {
            "role": "assistant",
            "content": "안녕하세요, 한국 법률 상담을 도와드리는 Lexi입니다. 필요하신 내용을 말씀해 주세요!",
        }
    ]
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


if not st.session_state.conversations_loaded:
    refresh_conversation_list()

st.markdown('<h1 class="main-header">법률 도우미 Lexi</h1>', unsafe_allow_html=True)
st.markdown('<div class="lexi-columns-marker"></div>', unsafe_allow_html=True)
left_col, right_col = st.columns([0.15, 0.85], gap="small")

with left_col:
    with st.container(height=1000, border=False):
        if st.button(
            "새 채팅", key="left-new-chat", use_container_width=True, type="primary"
        ):
            reset_conversation()
            st.rerun()
        st.markdown('<div class="sidebar-title">세션 정보</div>', unsafe_allow_html=True)
        render_session_panel()
        st.markdown('<div class="sidebar-title">채팅 로그</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-search">', unsafe_allow_html=True)
        st.text_input(
            "검색",
            key="conversation_search",
            placeholder="대화목록 검색하기",
            label_visibility="collapsed",
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-log-list scrollable">', unsafe_allow_html=True)
        conversations = st.session_state.conversation_list
        search_term = (st.session_state.get("conversation_search") or "").strip().lower()
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
                        "저장", key=f"rename-save-{conv['id']}", use_container_width=True
                    ):
                        rename_conversation(conv["id"], new_title)
                    if cancel_col.button(
                        "취소", key=f"rename-cancel-{conv['id']}", use_container_width=True
                    ):
                        cancel_rename()
                row.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Determine current conversation title
current_title = "New chat"
if st.session_state.conversation_id:
    for conv in st.session_state.conversation_list:
        if conv["id"] == st.session_state.conversation_id:
            current_title = conv.get("title") or current_title
            break

with right_col:
    with st.container(height=1200, border=False):
        header_cols = st.columns([0.7, 0.3])
        header_cols[0].markdown(
            f"""
            <div>
                <div class="workspace-eyebrow">LEXI WORKSPACE</div>
                <div class="workspace-title">{current_title}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if header_cols[1].button("새 채팅", key="right-new-chat", use_container_width=True):
            reset_conversation()
            st.rerun()
        chat_started = any(msg["role"] == "user" for msg in st.session_state.messages)
        st.markdown('<div class="conversation-body scrollable">', unsafe_allow_html=True)
        if chat_started:
            for message in st.session_state.messages:
                render_message(message)
        else:
            st.markdown(
                """
                <div class="hero-state">
                    <p class="workspace-eyebrow">Gemini 스타일 레이아웃</p>
                    <h1 class="hero-greeting">안녕하세요, <span class="hero-name">Lexi</span></h1>
                    <p>법률 관련 질문을 입력해 보세요. 필요한 자료를 함께 찾아드릴게요.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)
        if prompt := st.chat_input("Lexi에게 물어보기"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Contacting Lexi…"):
                try:
                    backend_response = call_backend(prompt)
                except requests.RequestException as exc:
                    st.error(f"Backend error: {exc}")
                else:
                    st.session_state.disclaimer = backend_response.get("disclaimer", "")
                    st.session_state.session_meta = {
                        "model": backend_response.get("model", "미상"),
                        "generation_config": backend_response.get("generation_config", {}),
                        "usage": backend_response.get("usage", {}),
                    }
                    st.session_state.messages.append(
                        {"role": "assistant", "content": backend_response["reply"]}
                    )
                    st.session_state.conversation_id = backend_response.get(
                        "conversation_id", st.session_state.get("conversation_id")
                    )
                    refresh_conversation_list()
            st.rerun()

if st.session_state.disclaimer:
    st.info(st.session_state.disclaimer)
