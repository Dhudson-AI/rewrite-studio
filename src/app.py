import textwrap

import streamlit as st

from prompts import REWRITE_SYSTEM_PROMPT, SUMMARY_SYSTEM_PROMPT
from services.openai_client import chat_completion


def inject_premium_style() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top, #f9fafb 0, #e5e7eb 45%, #d1d5db 100%);
            color: #111827;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .app-card {
            max-width: 980px;
            margin: 2.5rem auto 4rem auto;
            padding: 1.75rem 2rem 2rem 2rem;
            border-radius: 18px;
            background: rgba(249, 250, 251, 0.92);
            box-shadow:
                0 24px 60px rgba(15, 23, 42, 0.22),
                0 0 0 1px rgba(148, 163, 184, 0.35);
            backdrop-filter: blur(16px);
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
            margin-bottom: 1.4rem;
        }

        .mode-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.8rem;
            margin-right: 0.4rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 500;
            border: 1px solid transparent;
            background: #e5e7eb;
            color: #374151;
        }

        .mode-pill.active {
            background: linear-gradient(120deg, #4f46e5, #6366f1);
            color: white;
            box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.35);
        }

        .footer-note {
            font-size: 0.78rem;
            color: #6b7280;
            margin-top: 1.6rem;
            text-align: right;
        }

        .stTextArea label {
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def main() -> None:
    st.set_page_config(
        page_title="Rewrite Studio",
        page_icon="✍️",
        layout="wide",
    )

    inject_premium_style()

    with st.container():
        st.markdown('<div class="app-card">', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="app-title">Rewrite Studio</div>
            <div class="app-subtitle">
                Paste text, choose a mode, and let the model handle the rewriting or summarization.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_mode, _ = st.columns([1.2, 1])
        with col_mode:
            mode = st.radio(
                "Mode",
                ["Rewrite", "Summarize"],
                horizontal=True,
                index=0,
            )

        st.markdown(
            f"""
            <div style="margin-top: 0.2rem; margin-bottom: 0.6rem;">
                <span class="mode-pill {'active' if mode == 'Rewrite' else ''}">Rewrite</span>
                <span class="mode-pill {'active' if mode == 'Summarize' else ''}">Summarize</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns([1.1, 0.9])

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
                    help="How should the text feel after rewriting",
                )
                extra_label = f"Tone: {tone}"
            else:
                length = st.selectbox(
                    "Summary length",
                    ["Short", "Medium", "Detailed"],
                    index=0,
                    help="How long should the summary be",
                )
                extra_label = f"Length: {length}"

            run_clicked = st.button(
                "Generate",
                type="primary",
                use_container_width=True,
            )

        with col_right:
            st.markdown("#### Output")
            placeholder = st.empty()

            if run_clicked:
                if not text.strip():
                    placeholder.warning("Please add some text first.")
                else:
                    with st.spinner("Talking to the model..."):
                        try:
                            if mode == "Rewrite":
                                result = build_rewrite(text, tone)
                            else:
                                result = build_summary(text, length)

                            wrapped = textwrap.fill(result, width=88)
                            placeholder.markdown(f"```text\n{wrapped}\n```")
                        except Exception as exc:
                            placeholder.error(
                                "Something went wrong while calling the OpenAI API. "
                                "Check your API key and try again."
                            )
                            st.exception(exc)
            else:
                placeholder.info(
                    "Your result will appear here after you click Generate."
                )

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
