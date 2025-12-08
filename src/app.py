import html
import textwrap
import re

import streamlit as st

from prompts import REWRITE_SYSTEM_PROMPT, SUMMARY_SYSTEM_PROMPT
from services.openai_client import chat_completion


# --------------------------
# Styling
# --------------------------
def inject_premium_style() -> None:
    st.markdown(
        """
        <style>
        /* App background and typography */
        .stApp {
            background: radial-gradient(circle at 0% 0%, #f9fafb 0, #e5e7eb 42%, #d1d5db 100%);
            color: #111827;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .app-shell {
            max-width: 1180px;
            margin: 2.2rem auto 4rem auto;
        }

        .app-title {
            font-size: 1.9rem;
            font-weight: 650;
            letter-spacing: 0.02em;
            margin-bottom: 0.15rem;
        }

        .app-subtitle {
            font-size: 0.98rem;
            color: #6b7280;
            margin-bottom: 1.6rem;
        }

        /* Input text area card so it matches the output card */
        div[data-testid="stTextArea"] {
            border-radius: 18px;
            background: rgba(249, 250, 251, 0.96);
            box-shadow:
                0 20px 55px rgba(15, 23, 42, 0.18),
                0 0 0 1px rgba(148, 163, 184, 0.28);
            padding: 1.1rem 1.25rem 1.4rem 1.25rem;
        }

        div[data-testid="stTextArea"] > label {
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            color: #4b5563 !important;
            margin-bottom: 0.4rem !important;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 12px !important;
            border: 1px solid #e5e7eb !important;
            background: #f9fafb !important;
            box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.04) !important;
            font-size: 0.9rem !important;
        }

        /* Select boxes */
        div[data-baseweb="select"] > div {
            border-radius: 999px !important;
            border: 1px solid #e5e7eb !important;
            box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.7);
            background: rgba(249, 250, 251, 0.96);
        }

        /* Output card */
        .panel-output {
            border-radius: 18px;
            background: rgba(249, 250, 251, 0.96);
            box-shadow:
                0 20px 55px rgba(15, 23, 42, 0.18),
                0 0 0 1px rgba(148, 163, 184, 0.28);
            padding: 1.1rem 1.25rem 1.4rem 1.25rem;
        }

        .panel-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #4b5563;
            margin-bottom: 0.5rem;
        }

        .panel-body {
            font-size: 0.9rem;
            color: #111827;
        }

        @keyframes floatIn {
            from {
                opacity: 0;
                transform: translateY(8px) scale(0.985);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .panel-output-filled {
            animation: floatIn 220ms ease-out;
        }

        /* Generate button styling */
        .stButton > button {
            border-radius: 999px !important;
            border: none !important;
            background: linear-gradient(90deg, #fed7aa, #fdba74, #fb923c) !important;
            box-shadow:
                0 18px 40px rgba(248, 113, 22, 0.32),
                0 0 0 1px rgba(251, 146, 60, 0.7);
            color: #111827 !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em;
            height: 46px;
            transition: all 120ms ease-out;
        }

        .stButton > button:hover {
            filter: brightness(1.03);
            transform: translateY(-1px);
            box-shadow:
                0 22px 48px rgba(248, 113, 22, 0.42),
                0 0 0 1px rgba(251, 146, 60, 0.9);
        }

        .stButton > button:active {
            transform: translateY(0);
            box-shadow:
                0 12px 30px rgba(248, 113, 22, 0.3),
                0 0 0 1px rgba(251, 146, 60, 0.9);
        }

        .footer-note {
            font-size: 0.78rem;
            color: #6b7280;
            margin-top: 1.2rem;
            text-align: right;
        }

        .output-text {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            line-height: 1.5;
        }

        .output-placeholder {
            color: #9ca3af;
            font-style: italic;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------
# Model helpers
# --------------------------
def build_rewrite(text: str, tone: str) -> str:
    system_message = {"role": "system", "content": REWRITE_SYSTEM_PROMPT}
    user_message = {"role": "user", "content": f'Tone: "{tone}".\n\nText:\n{text}'}
    return chat_completion([system_message, user_message], temperature=0.75)


def build_summary(text: str, length: str) -> str:
    system_message = {"role": "system", "content": SUMMARY_SYSTEM_PROMPT}
    user_message = {
        "role": "user",
        "content": f'Summary length: "{length}".\n\nText:\n{text}',
    }
    return chat_completion([system_message, user_message], temperature=0.5)


def clean_dashes_and_fix_punctuation(text: str) -> str:
    """
    Remove wide dashes and replace them with commas, keep normal hyphens.
    """
    cleaned = text

    # Replace en and em type dashes (with or without spaces) with a comma and a space
    cleaned = re.sub(r"\s*[\u2013\u2014]\s*", ", ", cleaned)

    # Collapse multiple spaces
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    # Fix spacing before commas: " word ," -> " word,"
    cleaned = re.sub(r"\s+,", ",", cleaned)

    # Avoid double commas: ", ," -> ", "
    cleaned = re.sub(r",\s*,", ", ", cleaned)

    return cleaned.strip()


def render_output_panel(content: str | None) -> str:
    if content and content.strip():
        escaped = html.escape(textwrap.fill(content.strip(), width=90))
        body = f'<div class="output-text">{escaped}</div>'
        extra_class = "panel-output-filled"
    else:
        body = '<div class="output-placeholder">Your result will appear here after you click Generate.</div>'
        extra_class = ""

    return f"""
        <div class="panel-output {extra_class}">
            <div class="panel-title">Output</div>
            <div class="panel-body">
                {body}
            </div>
        </div>
    """


# --------------------------
# Streamlit app
# --------------------------
def main() -> None:
    st.set_page_config(
        page_title="Rewrite Studio",
        page_icon="✍️",
        layout="wide",
    )

    inject_premium_style()

    with st.container():
        st.markdown('<div class="app-shell">', unsafe_allow_html=True)

        # Header
        st.markdown(
            """
            <div class="app-title">Rewrite Studio</div>
            <div class="app-subtitle">
                Paste text, choose a mode, and let the model handle the rewriting or summarization.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Mode toggle
        col_mode, _ = st.columns([1.2, 1])
        with col_mode:
            mode = st.radio(
                "Mode",
                ["Rewrite", "Summarize"],
                horizontal=True,
                index=0,
            )

        # Two main columns
        col_left, col_right = st.columns([1.1, 0.95])

        # Left side: input and controls
        with col_left:
            default_example = (
                "Thank you for taking the time to consider my application. "
                "I am excited about the chance to contribute and learn from the team."
            )

            text = st.text_area(
                "Input text",
                value=default_example,
                height=220,
            )

            if mode == "Rewrite":
                tone = st.selectbox(
                    "Target tone",
                    ["Friendly", "Confident", "Concise", "Playful"],
                    index=1,
                    help="How should the text feel after rewriting?",
                )
                extra_label = f"Tone: {tone}"
                length = None
            else:
                length = st.selectbox(
                    "Summary length",
                    ["Short", "Medium", "Detailed"],
                    index=1,
                    help="How long should the summary be?",
                )
                extra_label = f"Length: {length}"
                tone = None

            st.markdown('<div class="generate-wrap">', unsafe_allow_html=True)
            run_clicked = st.button("Generate", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Right side: output card
        with col_right:
            placeholder = st.empty()

        result_text: str | None = None

        if run_clicked:
            if not text.strip():
                with col_right:
                    placeholder.markdown(
                        render_output_panel("Please add some text first."),
                        unsafe_allow_html=True,
                    )
            else:
                with col_right:
                    with st.spinner("Talking to the model..."):
                        try:
                            if mode == "Rewrite":
                                result_text = build_rewrite(text, tone)  # type: ignore[arg-type]
                            else:
                                result_text = build_summary(text, length)  # type: ignore[arg-type]
                        except Exception as exc:
                            placeholder.markdown(
                                render_output_panel(
                                    "Something went wrong while calling the OpenAI API. "
                                    "Check your API key and try again."
                                ),
                                unsafe_allow_html=True,
                            )
                            st.exception(exc)

        with col_right:
            if result_text is not None:
                cleaned = clean_dashes_and_fix_punctuation(result_text)
                placeholder.markdown(
                    render_output_panel(cleaned),
                    unsafe_allow_html=True,
                )
            elif not run_clicked:
                placeholder.markdown(
                    render_output_panel(None),
                    unsafe_allow_html=True,
                )

        # Footer
        st.markdown(
            f"""
            <div class="footer-note">
                Mode: <strong>{mode}</strong> • {extra_label}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
