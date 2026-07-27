"""About page: project overview for reviewers/interviewers."""
from __future__ import annotations

import streamlit as st


def render():
    st.markdown(
        """
        <div class="main-header">
            <h1>ℹ About This Project</h1>
            <p>AI Incoming Request Processing Workflow — Firstsource POC</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
This project demonstrates an **agentic AI request-processing pipeline** for a
customer support desk. It routes an incoming customer request through
classification, entity extraction, confidence-gated review, and a
deterministic business workflow.

### Core flow (required)
Single Request → Gemini → Workflow Manager → Response → Database

### Optional enhancement
CSV Upload → Batch Manager → Parallel Gemini Calls (ThreadPoolExecutor)
→ Workflow Manager → Database → Dashboard

### Why this design
- **AI reasoning** — Gemini classifies category & urgency, extracts entities,
  and produces a confidence score with a short rationale.
- **Agent orchestration** — a supervisor step (Gemini) hands off to a
  deterministic Workflow Manager, which decides routing and business actions.
- **Governance** — requests below the configured confidence threshold are
  automatically flagged for human review instead of being silently trusted.
- **Observability** — every processed request is logged to SQLite and
  surfaced on the Request History and Dashboard pages.
- **Extensibility** — batch size, parallel workers, and the confidence
  threshold are all configuration values, not hard-coded constants.

### Project structure
```
firstsource_poc/
├── app.py                     # Streamlit entrypoint & navigation
├── config/agent_config.py     # All tunables (model, thresholds, batch size)
├── core/
│   ├── schemas.py             # Pydantic validation of Gemini's JSON output
│   ├── prompts.py             # Single & batch prompt templates
│   ├── gemini_client.py       # Gemini API calls + JSON parsing/validation
│   ├── workflow_manager.py    # Deterministic routing & business actions
│   ├── batch_processor.py     # Parallel batch processing (ThreadPoolExecutor)
│   ├── database.py            # SQLite persistence
│   └── logger.py              # Centralised logging
├── ui/                        # One module per Streamlit page
└── data/sample_emails.csv     # Sample CSV for the batch demo
```

### Notes on batch processing cost
Batching reduces the *number* of API calls and network overhead, and can
improve throughput significantly. Whether it lowers your total bill still
depends on the provider's token-based pricing and the size of each batch —
it is not a guarantee, so this app presents it as an efficiency and
scalability enhancement rather than a cost promise.
        """
    )
