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
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0 0 1rem;
    }
    .main-header-logo {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        object-fit: contain;
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