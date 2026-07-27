"""
Home page — the primary demo surface.

Mode 1 (required by the assignment): single request typed in manually.
Mode 2 (optional enhancement): CSV upload processed in parallel batches.
"""
from __future__ import annotations

import uuid
from dataclasses import replace
from datetime import datetime

import pandas as pd
import streamlit as st

from config.agent_config import GEMINI_CONFIG, BATCH_CONFIG, SAMPLE_REQUESTS
from core import database
from core.batch_processor import emails_from_dataframe, process_emails_in_batches
from core.gemini_client import GeminiClientError, analyse_single_request
from core.prompts import build_single_prompt
from core.schemas import SchemaValidationError
from core.workflow_manager import execute_workflow


def _new_request_id() -> str:
    return f"REQ-{uuid.uuid4().hex[:5].upper()}"


def _active_gemini_config():
    """Use a session key when supplied; otherwise retain the .env fallback."""
    session_key = st.session_state.get("gemini_api_key", "").strip()
    return replace(GEMINI_CONFIG, api_key=session_key) if session_key else GEMINI_CONFIG


def _render_gemini_config_panel():
    with st.expander("⚙ Gemini Configuration (from agent_config.py)", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Model", GEMINI_CONFIG.model)
        c1.metric("Temperature", GEMINI_CONFIG.temperature)
        c2.metric("Top P", GEMINI_CONFIG.top_p)
        c2.metric("Max Tokens", GEMINI_CONFIG.max_output_tokens)
        c3.metric("Confidence Threshold", f"{GEMINI_CONFIG.confidence_threshold:.0%}")


def _render_single_result(request_id, customer_name, analysis, workflow_result):
    st.markdown('<div class="section-title">✅ AI Analysis Summary</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Category", analysis.category)
    c2.metric("Urgency", analysis.urgency)
    c3.metric("Department", workflow_result.department)

    st.markdown("**Confidence Score**")
    st.progress(min(max(analysis.confidence, 0.0), 1.0))
    st.caption(f"{analysis.confidence:.0%}")

    if workflow_result.requires_human_review:
        st.markdown(
            '<div class="warning-banner">⚠ Low confidence. Recommend human review.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">🧠 Reasoning</div>', unsafe_allow_html=True)
    st.info(analysis.reason)

    st.markdown('<div class="section-title">📎 Extracted Information</div>', unsafe_allow_html=True)
    entities_dict = analysis.entities.model_dump()
    st.table(pd.DataFrame(list(entities_dict.items()), columns=["Field", "Value"]))

    st.markdown('<div class="section-title">✉ AI Draft Response</div>', unsafe_allow_html=True)
    st.text_area("Draft response", analysis.draft_response, height=140, label_visibility="collapsed")

    st.markdown('<div class="section-title">⚡ Workflow Execution</div>', unsafe_allow_html=True)
    chips = "".join(f'<span class="step-chip">✓ {s}</span>' for s in workflow_result.steps)
    st.markdown(chips, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🏢 Business Actions</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(workflow_result.business_actions))

    st.markdown('<div class="section-title">📋 Final Summary</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Request ID", request_id)
    c2.metric("Status", "Human Review" if workflow_result.requires_human_review else "Completed")
    c3.metric("Workflow", workflow_result.workflow_name)
    c4.metric("Processing Time", f"{workflow_result.processing_time_seconds}s")


def _process_single_request(customer_name, customer_email, request_text):
    request_id = _new_request_id()
    gemini_config = _active_gemini_config()
    try:
        analysis = analyse_single_request(
            customer_name, customer_email, request_text, gemini_config, build_single_prompt
        )
    except (GeminiClientError, SchemaValidationError) as exc:
        st.error(f"Analysis failed: {exc}")
        return

    workflow_result = execute_workflow(
        category=analysis.category,
        urgency=analysis.urgency,
        confidence=analysis.confidence,
        confidence_threshold=gemini_config.confidence_threshold,
        gemini_department=analysis.department,
    )

    database.insert_request(
        {
            "request_id": request_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "request_text": request_text,
            "category": analysis.category,
            "urgency": analysis.urgency,
            "department": workflow_result.department,
            "confidence": analysis.confidence,
            "entities_json": analysis.entities.model_dump(),
            "draft_response": analysis.draft_response,
            "reason": analysis.reason,
            "workflow_name": workflow_result.workflow_name,
            "requires_review": int(workflow_result.requires_human_review),
            "status": "Human Review" if workflow_result.requires_human_review else "Completed",
            "processing_time_sec": workflow_result.processing_time_seconds,
            "source": "single",
        }
    )

    _render_single_result(request_id, customer_name, analysis, workflow_result)


def _load_sample_request(sample: str) -> None:
    """Populate the request widget before Streamlit renders it on the next run."""
    st.session_state["request_text"] = sample


def _render_single_request_tab():
    st.markdown('<div class="section-title">👤 Customer Details</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    customer_name = c1.text_input("Customer Name", key="cust_name")
    customer_email = c2.text_input("Customer Email", key="cust_email")
    st.caption(f"Request ID will be auto-generated · {datetime.now().strftime('%d %b %Y, %H:%M')}")

    st.markdown('<div class="section-title">📝 Customer Request</div>', unsafe_allow_html=True)
    request_text = st.text_area(
        "Customer Request", key="request_text", height=140,
        placeholder="e.g. I was charged twice for my broadband bill. Please refund the extra payment immediately.",
        label_visibility="collapsed",
    )

    st.caption("Example Requests")
    cols = st.columns(4)
    for col, (label, sample) in zip(cols, SAMPLE_REQUESTS.items()):
        col.button(
            label,
            key=f"sample_{label}",
            on_click=_load_sample_request,
            args=(sample,),
            width="stretch",
        )

    _render_gemini_config_panel()

    if st.button("Analyse request", type="primary", width="stretch"):
        if not customer_name or not customer_email or not request_text.strip():
            st.warning("Please fill in customer name, email, and the request text.")
        else:
            with st.spinner("Analysing request..."):
                _process_single_request(customer_name, customer_email, request_text)


def _render_batch_tab():
    st.caption(
        "Upload a CSV of customer emails (columns: Customer, Email, Subject, Body). "
        "Requests are grouped into batches and analysed in parallel."
    )

    with open("data/sample_emails.csv", "rb") as f:
        st.download_button("⬇ Download sample CSV", f, file_name="sample_emails.csv", mime="text/csv")

    uploaded = st.file_uploader("Upload Emails (.csv)", type=["csv"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Batch Size", BATCH_CONFIG.batch_size)
    c2.metric("Max Parallel Workers", BATCH_CONFIG.max_parallel_workers)
    c3.metric("Batch Processing", "Enabled" if BATCH_CONFIG.enable_batch_processing else "Disabled")

    if uploaded is not None and st.button("Process emails", type="primary", width="stretch"):
        df = pd.read_csv(uploaded)
        emails = emails_from_dataframe(df)
        gemini_config = _active_gemini_config()

        with st.spinner(f"Processing {len(emails)} emails across parallel batches..."):
            results, errors = process_emails_in_batches(emails, gemini_config, BATCH_CONFIG)

        for err in errors:
            st.error(err)

        if not results:
            st.warning("No requests were successfully analysed.")
            return

        rows = []
        for r in results:
            workflow_result = execute_workflow(
                category=r.category,
                urgency=r.urgency,
                confidence=r.confidence,
                confidence_threshold=gemini_config.confidence_threshold,
                gemini_department=r.department,
            )
            database.insert_request(
                {
                    "request_id": r.request_id,
                    "customer_name": r.customer_name,
                    "customer_email": "",
                    "request_text": "",
                    "category": r.category,
                    "urgency": r.urgency,
                    "department": workflow_result.department,
                    "confidence": r.confidence,
                    "entities_json": r.entities.model_dump(),
                    "draft_response": r.draft_response,
                    "reason": r.reason,
                    "workflow_name": workflow_result.workflow_name,
                    "requires_review": int(workflow_result.requires_human_review),
                    "status": "Human Review" if workflow_result.requires_human_review else "Completed",
                    "processing_time_sec": workflow_result.processing_time_seconds,
                    "source": "batch",
                }
            )
            rows.append(
                {
                    "Request": r.request_id,
                    "Customer": r.customer_name,
                    "Category": r.category,
                    "Urgency": r.urgency,
                    "Confidence": f"{r.confidence:.0%}",
                    "Department": workflow_result.department,
                    "Status": "Human review" if workflow_result.requires_human_review else "Completed",
                }
            )

        st.markdown('<div class="section-title">📊 Batch Results</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(rows), hide_index=True)

        st.markdown('<div class="section-title">🔎 Request Details</div>', unsafe_allow_html=True)
        for r in results:
            with st.expander(f"{r.request_id} — {r.customer_name} ({r.category}, {r.urgency})"):
                st.write(f"**Confidence:** {r.confidence:.0%}")
                st.write(f"**Reason:** {r.reason}")
                st.write("**Entities:**", r.entities.model_dump())
                st.text_area("Draft Response", r.draft_response, height=100, key=f"draft_{r.request_id}")


def render():
    st.markdown(
        """
        <div class="main-header">
            <h1>AI Incoming Request Processing</h1>
            <p>Firstsource POC Demonstration — Agentic AI Engineer Assignment</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["📋 Single Request", "📁 Batch Upload (CSV)"])
    with tab1:
        _render_single_request_tab()
    with tab2:
        _render_batch_tab()
