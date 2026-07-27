"""Configuration page: transparently shows the settings driving the agent.

Values are read directly from config/agent_config.py (and therefore from
environment variables / .env), so this page can never drift from what
the app is actually running with.
"""
from __future__ import annotations

import streamlit as st

from config.agent_config import BATCH_CONFIG, CATEGORIES, GEMINI_CONFIG, URGENCY_LEVELS


def render():
    st.markdown(
        """
        <div class="main-header">
            <h1>⚙ Configuration</h1>
            <p>Live settings loaded from config/agent_config.py</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Gemini Settings</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Model", GEMINI_CONFIG.model)
    c1.metric("Temperature", GEMINI_CONFIG.temperature)
    c2.metric("Top P", GEMINI_CONFIG.top_p)
    c2.metric("Max Output Tokens", GEMINI_CONFIG.max_output_tokens)
    c3.metric("Confidence Threshold", f"{GEMINI_CONFIG.confidence_threshold:.0%}")
    active_key = st.session_state.get("gemini_api_key", "").strip() or GEMINI_CONFIG.api_key
    c3.metric("API key set", "Yes" if active_key else "No — enter a key in the sidebar")

    st.markdown('<div class="section-title">Batch Processing Settings</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Enabled", "Yes" if BATCH_CONFIG.enable_batch_processing else "No")
    c2.metric("Batch Size", BATCH_CONFIG.batch_size)
    c3.metric("Max Parallel Workers", BATCH_CONFIG.max_parallel_workers)
    c4.metric("Max Batch Requests", BATCH_CONFIG.max_batch_requests)

    st.markdown('<div class="section-title">Taxonomy</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.write("**Categories**")
    c1.write("\n".join(f"- {c}" for c in CATEGORIES))
    c2.write("**Urgency Levels**")
    c2.write("\n".join(f"- {u}" for u in URGENCY_LEVELS))

    st.caption(
        "To change these values, edit `.env` (see `.env.example`) or "
        "`config/agent_config.py`, then restart the app."
    )
