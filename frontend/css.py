from __future__ import annotations
from string import Template
THEME_CHOICES = {
    "라이트": "light",
    "다크": "dark",
}

THEME_PALETTES = {
    "light": {
        "app_bg": "#f4f7fb",
        "panel_bg": "#ffffff",
        "panel_border": "rgba(15, 23, 42, 0.08)",
        "panel_shadow": "0 8px 30px rgba(15, 23, 42, 0.08)",
        "workspace_bg": "#ffffff",
        "workspace_border": "rgba(15, 23, 42, 0.06)",
        "workspace_shadow": "0 30px 90px rgba(15, 23, 42, 0.08)",
        "text_primary": "#0b1533",
        "text_secondary": "#6b7a99",
        "accent": "#276ef1",
        "chat_user_bg": "linear-gradient(135deg, rgba(39, 110, 241, 0.12), rgba(39, 110, 241, 0.05))",
        "chat_assistant_bg": "linear-gradient(135deg, rgba(3, 168, 124, 0.16), rgba(3, 168, 124, 0.05))",
        "bubble_border": "rgba(15, 23, 42, 0.08)",
        "bubble_shadow": "0 14px 30px rgba(15, 23, 42, 0.08)",
        "input_bg": "#ffffff",
        "input_border": "rgba(15, 23, 42, 0.12)",
    },
    "dark": {
        "app_bg": "linear-gradient(180deg, #030711 0%, #050d1f 40%, #020512 100%)",
        "panel_bg": "rgba(8, 19, 45, 0.9)",
        "panel_border": "rgba(70, 96, 140, 0.3)",
        "panel_shadow": "0 15px 45px rgba(0, 0, 0, 0.55)",
        "workspace_bg": "rgba(5, 13, 30, 0.95)",
        "workspace_border": "rgba(58, 95, 170, 0.25)",
        "workspace_shadow": "0 35px 80px rgba(0, 0, 0, 0.65)",
        "text_primary": "#e6edff",
        "text_secondary": "#8ea0c9",
        "accent": "#72a8ff",
        "chat_user_bg": "linear-gradient(135deg, rgba(92, 141, 255, 0.25), rgba(92, 141, 255, 0.08))",
        "chat_assistant_bg": "linear-gradient(135deg, rgba(255, 255, 255, 0.18), rgba(255, 255, 255, 0.05))",
        "bubble_border": "rgba(255, 255, 255, 0.08)",
        "bubble_shadow": "0 18px 40px rgba(0, 0, 0, 0.55)",
        "input_bg": "rgba(4, 12, 28, 0.9)",
        "input_border": "rgba(114, 168, 255, 0.3)",
    },
}

CSS_TEMPLATE = Template("""
<style>
:root {{
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
}}
html, body {{
    min-height: 100%;
    background: var(--app-bg);
}}
body, .block-container {{
    background: transparent;
    color: var(--text-primary);
    font-family: 'Pretendard', 'Inter', 'Noto Sans KR', sans-serif;
}}
div[data-testid="stAppViewContainer"] {{
    background: var(--app-bg);
    overflow-y: auto;
}}
div[data-testid="stAppViewContainer"] > .main {{
    width: min(var(--layout-max-width), 100%);
    margin: 0 auto;
    padding: 1rem 0 4rem;
    position: relative;
}}
header[data-testid="stHeader"] {{
    display: none;
}}
.block-container {{
    padding: 0 1.5rem 1.5rem;
}}
.lexi-columns-marker {{
    display: none;
}}
.lexi-columns-marker + div[data-testid="stColumns"] {{
    column-gap: 1.8rem;
    align-items: flex-start;
}}
.lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"] {{
    min-height: 0;
    height: auto !important;
}}
.lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"]:first-of-type > div[data-testid="stVerticalBlock"]:first-of-type {{
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    padding: 1.1rem 1.25rem;
    box-shadow: var(--panel-shadow);
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
}}
.lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"]:first-of-type {{
    background: var(--workspace-bg);
    border: 1px solid var(--workspace-border);
    border-radius: 28px;
    padding: 1.5rem 2rem 6.5rem;
    box-shadow: var(--workspace-shadow);
    min-height: 0;
    position: relative;
    overflow: hidden;
}}
.lexi-columns-marker + div[data-testid="stColumns"] > div[data-testid="column"]:nth-of-type(2) > div[data-testid="stVerticalBlock"]:first-of-type > div:first-child {{
    width: 100%;
}}
.sidebar-header {{
    display: flex;
    align-items: center;
    gap: 0.65rem;
}}
.sidebar-logo {{
    width: 38px;
    height: 38px;
    border-radius: 12px;
    object-fit: contain;
    border: 1px solid rgba(255,255,255,0.15);
}}
.sidebar-headline {{
    font-weight: 700;
    font-size: 1.05rem;
}}
.sidebar-subtitle {{
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: -2px;
}}
/* .theme-toggle {{
    background: rgba(39, 110, 241, 0.04);
    border-radius: 16px;
    padding: 0.4rem 0.7rem 0.1rem;
    border: 1px solid rgba(39, 110, 241, 0.12);
}}
.theme-toggle label {{
    color: var(--text-secondary) !important;
}} */
.sidebar-title {{
    font-size: 0.92rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}}
.session-card {{
    background: rgba(255, 255, 255, 0.04);
    border-radius: 14px;
    border: 1px solid var(--panel-border);
    padding: 0.9rem;
    color: var(--text-primary);
}}
.session-card small {{
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--text-secondary);
}}
.session-headline {{
    font-size: 1.05rem;
    font-weight: 700;
    margin-top: 0.15rem;
}}
.session-metrics {{
    display: flex;
    gap: 0.75rem;
    margin-top: 0.6rem;
}}
.session-metrics div {{
    flex: 1;
    font-size: 0.85rem;
    color: var(--text-secondary);
}}
.session-metrics strong {{
    display: block;
    font-size: 1rem;
    color: var(--text-primary);
}}
.session-usage {{
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    margin-top: 0.6rem;
    color: var(--text-secondary);
}}
.session-usage strong {{
    color: var(--text-primary);
    margin-left: 0.3rem;
}}
.chat-log-list {{
    flex: 1;
    overflow-y: auto;
    padding-right: 0.3rem;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
}}
.chat-log-entry button {{
    width: 100%;
    border-radius: 14px;
    border: 1px solid transparent;
    background: rgba(255, 255, 255, 0.04);
    color: var(--text-primary);
    padding: 0.6rem 0.75rem;
    text-align: left;
    font-size: 0.9rem;
}}
.chat-log-entry.active button {{
    border-color: var(--accent);
    background: rgba(39, 110, 241, 0.1);
}}
.workspace-title {{
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}}
.conversation-shell {{
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}}
.conversation-body {{
    flex: 1;
    overflow-y: auto;
    padding-right: 0.35rem;
    padding-bottom: 4rem;
}}
.chat-bubble {{
    border-radius: 16px;
    padding: 0.75rem 1rem;
    margin: 0.35rem 0;
    max-width: 92%;
    display: inline-flex;
    gap: 0.55rem;
    border: 1px solid var(--bubble-border);
    box-shadow: var(--bubble-shadow);
    backdrop-filter: blur(6px);
}}
.chat-user {{
    background: var(--chat-user-bg);
}}
.chat-assistant {{
    background: var(--chat-assistant-bg);
}}
.avatar {{
    font-size: 1.3rem;
}}
.message-text {{
    line-height: 1.55;
}}
.hero-state {{
    margin-top: 10%;
    text-align: center;
    color: var(--text-secondary);
}}
.hero-state h1 {{
    font-size: 2rem;
    margin-bottom: 0.2rem;
}}
.hero-input-wrapper {{
    margin: 1.5rem auto 0;
    padding: 1.2rem 1.5rem 1.4rem;
    border: 1px solid var(--panel-border);
    border-radius: 24px;
    box-shadow: 0 20px 45px rgba(12, 23, 52, 0.12);
    background: var(--panel-bg);
    width: min(720px, 100%);
}}
.hero-input-wrapper div[data-testid="stTextArea"] textarea {{
    border-radius: 20px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    background: rgba(246, 248, 253, 0.95);
    color: #0b1533;
    font-size: 1rem;
    min-height: 120px;
}}
.hero-input-wrapper div[data-testid="stButton"] button {{
    margin-top: 0.9rem;
    height: 52px;
    border-radius: 18px;
    border: none;
    background: linear-gradient(115deg, #2d7df7, #54b0ff);
    color: #fff;
    font-weight: 700;
    letter-spacing: 0.04em;
    box-shadow: 0 18px 38px rgba(45, 125, 247, 0.35);
}}
.hero-input-wrapper {{
    margin: 1.2rem auto 0;
    padding: 1rem 1.3rem 1.25rem;
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    box-shadow: var(--panel-shadow);
    background: rgba(255, 255, 255, 0.08);
    width: min(640px, 100%);
}}
.hero-input-wrapper div[data-testid="stTextArea"] textarea {{
    border-radius: 16px;
    border: 1px solid var(--panel-border);
    background: #fff;
    color: #0b1533;
    font-size: 1rem;
}}
.hero-input-wrapper div[data-testid="stButton"] button {{
    margin-top: 0.7rem;
    height: 48px;
    border-radius: 14px;
    border: none;
    background: linear-gradient(115deg, #2d7df7, #54b0ff);
    color: #fff;
    font-weight: 600;
    letter-spacing: 0.03em;
    box-shadow: 0 14px 30px rgba(45, 125, 247, 0.35);
}}
div[data-testid="stChatInput"] {{
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
}}
div[data-testid="stChatInput"] textarea {{
    background: transparent;
    color: var(--text-primary);
}}
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
div[data-testid="stChatInput"] button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 20px 40px rgba(45, 126, 247, 0.4);
}}
.scrollable::-webkit-scrollbar {{
    width: 6px;
}}
.scrollable::-webkit-scrollbar-thumb {{
    background: rgba(120, 144, 180, 0.5);
    border-radius: 4px;
}}
</style>
""")


def get_theme_css(theme_key: str) -> str:
    palette = THEME_PALETTES.get(theme_key, THEME_PALETTES["light"])
    return CSS_TEMPLATE.substitute(**palette)