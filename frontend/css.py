from __future__ import annotations
from string import Template
THEME_CHOICES = {
    "라이트": "light",
    "다크": "dark",
}

THEME_PALETTES = {
    "light": {
        "app_bg": "#eef2fb",
        "panel_bg": "#f9fbff",
        "panel_border": "rgba(66, 99, 175, 0.2)",
        "panel_shadow": "0 12px 35px rgba(37, 69, 135, 0.05)",
        "workspace_bg": "#ffffff",
        "workspace_border": "rgba(66, 99, 175, 0.12)",
        "workspace_shadow": "0 35px 90px rgba(37, 69, 135, 0.08)",
        "text_primary": "#101828",
        "text_secondary": "#5c6b8f",
        "accent": "#2f7bff",
        "chat_user_bg": "linear-gradient(135deg, rgba(47, 123, 255, 0.18), rgba(47, 123, 255, 0.05))",
        "chat_assistant_bg": "linear-gradient(135deg, rgba(15, 188, 249, 0.16), rgba(253, 253, 255, 0.6))",
        "bubble_border": "rgba(47, 123, 255, 0.12)",
        "bubble_shadow": "0 18px 50px rgba(30, 64, 175, 0.08)",
        "input_bg": "#ffffff",
        "input_border": "rgba(66, 99, 175, 0.18)",
    },
    "dark": {
        "app_bg": "linear-gradient(180deg, #020617 0%, #051029 45%, #020818 100%)",
        "panel_bg": "rgba(7, 16, 38, 0.95)",
        "panel_border": "rgba(92, 123, 196, 0.35)",
        "panel_shadow": "0 18px 55px rgba(0, 0, 0, 0.65)",
        "workspace_bg": "rgba(4, 12, 31, 0.95)",
        "workspace_border": "rgba(95, 132, 214, 0.3)",
        "workspace_shadow": "0 40px 90px rgba(0, 0, 0, 0.7)",
        "text_primary": "#eaf1ff",
        "text_secondary": "#94a8d8",
        "accent": "#66a5ff",
        "chat_user_bg": "linear-gradient(135deg, rgba(102, 165, 255, 0.3), rgba(102, 165, 255, 0.08))",
        "chat_assistant_bg": "linear-gradient(135deg, rgba(21, 213, 255, 0.18), rgba(21, 213, 255, 0.05))",
        "bubble_border": "rgba(236, 246, 255, 0.1)",
        "bubble_shadow": "0 20px 50px rgba(1, 3, 10, 0.55)",
        "input_bg": "rgba(3, 9, 24, 0.9)",
        "input_border": "rgba(102, 165, 255, 0.32)",
    },
}

CSS_TEMPLATE = Template("""
<style>
:root {
    --app-bg: $app_bg;
    --panel-bg: $panel_bg;
    --panel-border: $panel_border;
    --panel-shadow: $panel_shadow;
    --workspace-bg: $workspace_bg;
    --workspace-border: $workspace_border;
    --workspace-shadow: $workspace_shadow;
    --text-primary: $text_primary;
    --text-secondary: $text_secondary;
    --accent: $accent;
    --chat-user-bg: $chat_user_bg;
    --chat-assistant-bg: $chat_assistant_bg;
    --bubble-border: $bubble_border;
    --bubble-shadow: $bubble_shadow;
    --input-bg: $input_bg;
    --input-border: $input_border;
    --layout-max-width: 1260px;
    --layout-width: min(var(--layout-max-width), 100vw);
}
html, body {
    min-height: 100%;
    background: var(--app-bg);
}
html {
    scrollbar-width: none;
}
html::-webkit-scrollbar {
    width: 0;
    height: 0;
}
body, .block-container {
    background: transparent;
    color: var(--text-primary);
    font-family: 'Pretendard', 'Inter', 'Noto Sans KR', sans-serif;
}
body {
    scrollbar-width: none;
}
body::-webkit-scrollbar {
    width: 0;
    height: 0;
}
div[data-testid="stAppViewContainer"] {
    background: var(--app-bg);
    height: 100vh;
    overflow: hidden;
}
div[data-testid="stAppViewContainer"] > .main {
    width: var(--layout-width);
    margin: 0 auto;
    padding: 1rem 0 4rem;
    position: relative;
    min-height: 100vh;
}
header[data-testid="stHeader"] {
    display: none;
}
.block-container {
    padding: 0 1.5rem 1.5rem;
}
.lexi-columns-marker {
    display: none;
}
.lexi-columns-marker + div[data-testid="stColumns"] {
    column-gap: 1.8rem;
    align-items: flex-start;
    min-height: calc(100vh - 40px);
}
.lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"] {
    min-height: 0;
    height: 100%;
}
.lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"]:first-of-type > div[data-testid="stVerticalBlock"]:first-of-type {
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    padding: 1.1rem 1.25rem;
    box-shadow: var(--panel-shadow);
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
    height: calc(100vh - 60px);
    max-height: calc(100vh - 60px);
    overflow: hidden;
}
.lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"]:first-of-type {
    background: var(--workspace-bg);
    border: 1px solid var(--workspace-border);
    border-radius: 28px;
    padding: 1.5rem 2rem 6.5rem;
    box-shadow: var(--workspace-shadow);
    min-height: 0;
    position: relative;
    overflow: hidden;
    height: calc(100vh - 60px);
    max-height: calc(100vh - 60px);
    display: flex;
    flex-direction: column;
}
.lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"]:first-of-type > div:first-child {
    width: 100%;
}
.sidebar-header {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}
.sidebar-logo {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    object-fit: contain;
    border: 1px solid rgba(255,255,255,0.15);
}
.sidebar-headline {
    font-weight: 700;
    font-size: 1.05rem;
}
.sidebar-subtitle {
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: -2px;
}
/* .theme-toggle {
    background: rgba(39, 110, 241, 0.04);
    border-radius: 16px;
    padding: 0.4rem 0.7rem 0.1rem;
    border: 1px solid rgba(39, 110, 241, 0.12);
}
.theme-toggle label {
    color: var(--text-secondary) !important;
} */
.sidebar-title {
    font-size: 0.92rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.session-card {
    background: rgba(255, 255, 255, 0.04);
    border-radius: 14px;
    border: 1px solid var(--panel-border);
    padding: 0.9rem;
    color: var(--text-primary);
}
.session-card small {
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--text-secondary);
}
.session-headline {
    font-size: 1.05rem;
    font-weight: 700;
    margin-top: 0.15rem;
}
.session-metrics {
    display: flex;
    gap: 0.75rem;
    margin-top: 0.6rem;
}
.session-metrics div {
    flex: 1;
    font-size: 0.85rem;
    color: var(--text-secondary);
}
.session-metrics strong {
    display: block;
    font-size: 1rem;
    color: var(--text-primary);
}
.session-usage {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    margin-top: 0.6rem;
    color: var(--text-secondary);
}
.session-usage strong {
    color: var(--text-primary);
    margin-left: 0.3rem;
}
.compare-model-list {
    list-style: none;
    padding: 0;
    margin: 0.8rem 0 0;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
.compare-model-list li {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    color: var(--text-secondary);
}
.compare-model-list li strong {
    color: var(--text-primary);
}
.compare-usage-table {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-top: 0.5rem;
}
.compare-usage-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    color: var(--text-secondary);
}
.compare-usage-row .token-stats {
    display: flex;
    gap: 0.5rem;
}
.compare-usage-row strong {
    color: var(--text-primary);
    font-size: 0.85rem;
}
.chat-log-list {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 0.3rem;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    min-height: 0;
}
.chat-log-list::-webkit-scrollbar {
    width: 4px;
}
.chat-log-list::-webkit-scrollbar-thumb {
    background: rgba(120, 144, 180, 0.5);
    border-radius: 4px;
}
.chat-log-entry button {
    width: 100%;
    border-radius: 14px;
    border: 1px solid transparent;
    background: rgba(255, 255, 255, 0.04);
    color: var(--text-primary);
    padding: 0.6rem 0.75rem;
    text-align: left;
    font-size: 0.9rem;
}
.chat-log-entry.active button {
    border-color: var(--accent);
    background: rgba(39, 110, 241, 0.1);
}
.workspace-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.conversation-shell {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.conversation-body {
    flex: 1;
    overflow-y: auto;
    padding-right: 0.35rem;
    padding-bottom: 4rem;
}
.chat-row[data-role="assistant"] {
    justify-content: flex-start;
}
.chat-row[data-role="user"] {
    justify-content: flex-end;
}
.chat-bubble {
    border-radius: 22px;
    padding: 0.55rem 0.95rem;
    margin: 0.2rem 0;
    max-width: 92%;
    display: inline-flex;
    flex-direction: column;
    gap: 0.25rem;
    border: 1px solid var(--bubble-border);
    box-shadow: var(--bubble-shadow);
    backdrop-filter: blur(7px);
}
.chat-bubble[data-variant] {
    max-width: 100%;
    width: 100%;
}
.chat-bubble.ping-bubble {
    animation: pingGlow 1.4s ease-in-out infinite;
}
.bubble-variant {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.ping-bubble .message-text::after {
    content: "";
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-left: 6px;
    background: var(--accent);
    animation: pingDot 1s ease-in-out infinite;
}
@keyframes pingDot {
    0% { opacity: 0.2; transform: translateY(0); }
    50% { opacity: 1; transform: translateY(-2px); }
    100% { opacity: 0.2; transform: translateY(0); }
}
@keyframes pingGlow {
    0% { box-shadow: 0 0 0 rgba(47, 123, 255, 0.22); }
    50% { box-shadow: 0 0 12px rgba(47, 123, 255, 0.35); }
    100% { box-shadow: 0 0 0 rgba(47, 123, 255, 0.22); }
}
.chat-user {
    background: var(--chat-user-bg);
}
.chat-assistant {
    background: var(--chat-assistant-bg);
}
.message-text {
    line-height: 1.4;
    white-space: pre-wrap;
}
.message-text p {
    margin: 0.2rem 0 0.15rem;
    line-height: 1.32;
}
.message-text p + p {
    margin-top: 0.15rem;
}
.message-text ul,
.message-text ol {
    margin: 0.15rem 0;
    padding-left: 0.9rem;
    line-height: 1.28;
    list-style-position: inside;
}
.message-text li {
    margin-bottom: 0.02rem;
    line-height: 1.25;
}
.compare-group {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.9rem;
    width: 100%;
    margin: 0.4rem 0;
    align-items: flex-start;
}
.compare-item {
    display: block;
}
.compare-group .chat-bubble {
    width: 100%;
    max-width: none;
}
.hero-state {
    margin-top: 10%;
    text-align: center;
    color: var(--text-secondary);
}
.hero-state h1 {
    font-size: 2rem;
    margin-bottom: 0.2rem;
}
.hero-state + div[data-testid="stChatInput"] {
    margin-top: 1.25rem;
}
div[data-testid="stChatInput"] {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    border-radius: 22px;
    border: 1px solid var(--input-border);
    background: var(--input-bg);
    box-shadow: 0 25px 45px rgba(5, 15, 35, 0.18);
}
body:not([data-hero-mode="true"]) div[data-testid="stChatInput"] {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    border-radius: 22px;
    border: 1px solid var(--input-border);
    background: var(--input-bg);
    box-shadow: 0 25px 45px rgba(5, 15, 35, 0.18);
    position: fixed;
    bottom: 24px;
    left: calc(50% + 0.13 * var(--layout-width));
    transform: translateX(-50%);
    width: min(760px, calc(0.74 * var(--layout-width)));
    margin: 0;
    z-index: 1000;
}

div[data-testid="stChatInput"] > label {
    display: none;
}

body[data-hero-mode="true"] div[data-testid="stChatInput"] {
    position: static;
    width: min(760px, calc(var(--layout-width) * 0.74));
    margin: 1.5rem auto 2rem;
    border-radius: 28px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    background: #ffffff;
    box-shadow: 0 25px 45px rgba(7, 19, 45, 0.12);
    gap: 0.6rem;
}
div[data-testid="stChatInput"] textarea {
    background: transparent;
    color: var(--text-primary);
    min-height: 52px;
    padding: 0.85rem 1.15rem;
    font-size: 1rem;
}
body[data-hero-mode="true"] div[data-testid="stChatInput"] textarea {
    background: #f6f8fc;
    color: #0b1533;
    border-radius: 20px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    box-shadow: inset 0 3px 12px rgba(12, 23, 52, 0.08);
}
div[data-testid="stChatInput"] button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.35rem;
    border: none;
    border-radius: 16px;
    padding: 0.45rem 1.6rem;
    background: linear-gradient(120deg, #2d7ef7, #57b2ff);
    color: #fff;
    font-weight: 600;
    letter-spacing: 0.03em;
    box-shadow: 0 16px 34px rgba(45, 126, 247, 0.35);
    margin-bottom: 5px;
}
div[data-testid="stChatInput"] button svg {
    display: none;
}
div[data-testid="stChatInput"] button::before {
    content: "";
    width: 18px;
    height: 18px;
    display: inline-block;
    background: url("data:image/svg+xml;utf8,%3Csvg%20width%3D%2718%27%20height%3D%2718%27%20viewBox%3D%270%200%2024%2024%27%20fill%3D%27none%27%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%3E%3Cpath%20d%3D%27M3%2011.5L21%203L14.5%2021L11%2013L3%2011.5Z%27%20stroke%3D%27white%27%20stroke-width%3D%272%27%20stroke-linejoin%3D%27round%27/%3E%3C/svg%3E") no-repeat center / contain;
}
div[data-testid="stChatInput"] button:hover {
    transform: translateY(-1px);
    box-shadow: 0 20px 40px rgba(45, 126, 247, 0.4);
}
body[data-hero-mode="true"] div[data-testid="stChatInput"] button {
    height: 52px;
    border-radius: 22px;
    font-weight: 700;
}
.scrollable::-webkit-scrollbar {
    width: 6px;
}
.scrollable::-webkit-scrollbar-thumb {
    background: rgba(120, 144, 180, 0.5);
    border-radius: 4px;
}
</style>
""")


def get_theme_css(theme_key: str) -> str:
    palette = THEME_PALETTES.get(theme_key, THEME_PALETTES["light"])
    return CSS_TEMPLATE.substitute(**palette)