"""Dashboard page: KPI cards and category/urgency breakdowns."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from core import database


def _kpi_card(col, label, value):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render():
    st.markdown(
        """
        <div class="main-header">
            <h1>📊 Dashboard</h1>
            <p>Live operational metrics across all processed requests.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpis = database.get_kpis()

    if kpis["total_requests"] == 0:
        st.info("No data yet. Process some requests on the Home page to populate the dashboard.")
        return

    row1 = st.columns(5)
    _kpi_card(row1[0], "Total Requests", kpis["total_requests"])
    _kpi_card(row1[1], "Successfully Processed", kpis["successfully_processed"])
    _kpi_card(row1[2], "Human Review Required", kpis["human_review_required"])
    _kpi_card(row1[3], "Avg. Confidence", f"{kpis['avg_confidence']:.0%}")
    _kpi_card(row1[4], "Avg. Processing Time", f"{kpis['avg_processing_time']}s")

    st.markdown('<div class="section-title">By Category / Urgency</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        cat_df = pd.DataFrame(
            list(kpis["by_category"].items()), columns=["Category", "Count"]
        )
        fig = px.bar(cat_df, x="Category", y="Count", color="Category", title="Requests by Category")
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, width="stretch")

    with c2:
        urg_df = pd.DataFrame(
            list(kpis["by_urgency"].items()), columns=["Urgency", "Count"]
        )
        fig = px.pie(urg_df, names="Urgency", values="Count", title="Requests by Urgency")
        fig.update_layout(height=350)
        st.plotly_chart(fig, width="stretch")

    st.markdown('<div class="section-title">Recent Requests</div>', unsafe_allow_html=True)
    recent = database.fetch_all()[:10]
    df = pd.DataFrame(recent)[["request_id", "customer_name", "category", "urgency", "status", "created_at"]]
    df.columns = ["Request ID", "Customer", "Category", "Urgency", "Status", "Date"]
    st.dataframe(df, hide_index=True)
