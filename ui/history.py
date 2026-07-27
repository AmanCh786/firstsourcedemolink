"""Request History page: browse and filter all previously processed requests."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from config.agent_config import CATEGORIES, URGENCY_LEVELS
from core import database


def render():
    st.markdown(
        """
        <div class="main-header">
            <h1>📋 Request History</h1>
            <p>All requests processed so far, single and batch alike.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    category = c1.selectbox("Category", ["All"] + CATEGORIES)
    urgency = c2.selectbox("Urgency", ["All"] + URGENCY_LEVELS)
    status = c3.selectbox("Status", ["All", "Completed", "Human Review"])

    rows = database.fetch_filtered(category=category, urgency=urgency, status=status)

    if not rows:
        st.info("No requests match the current filters yet. Process a request on the Home page first.")
        return

    df = pd.DataFrame(rows)[
        [
            "request_id", "customer_name", "category", "urgency",
            "confidence", "status", "department", "workflow_name", "created_at",
        ]
    ].rename(
        columns={
            "request_id": "Request ID",
            "customer_name": "Customer",
            "category": "Category",
            "urgency": "Urgency",
            "confidence": "Confidence",
            "status": "Status",
            "department": "Department",
            "workflow_name": "Workflow",
            "created_at": "Date",
        }
    )
    df["Confidence"] = df["Confidence"].apply(lambda x: f"{x:.0%}" if x is not None else "-")

    st.dataframe(df, hide_index=True)
    st.caption(f"Showing {len(df)} of {len(database.fetch_all())} total requests.")
