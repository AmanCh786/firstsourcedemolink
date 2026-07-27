"""Streamlit entry point for the request operations prototype."""
from __future__ import annotations

import streamlit as st

from core import database
from core.logger import setup_logging
from ui import about, configuration, dashboard, history, home

st.set_page_config(page_title="Firstsource | Request operations", page_icon=":material/account_tree:", layout="wide")
setup_logging()
database.init_db()

PAGES = {
    "Operations": home,
    "Request history": history,
    "Dashboard": dashboard,
    "Configuration": configuration,
    "About": about,
}

with st.sidebar:
    st.title("Firstsource")
    st.caption("Request operations prototype")
    selection = st.radio("Navigate", list(PAGES), label_visibility="collapsed")
    st.divider()
    with st.expander("Gemini connection"):
        st.text_input(
            "Gemini API key",
            type="password",
            key="gemini_api_key",
            placeholder="Paste your API key",
            help="Used only for this browser session. It is not saved to the database or project files.",
            persist_state="session",
        )
    st.caption("Gemini analysis with a SQLite audit trail")

PAGES[selection].render()
