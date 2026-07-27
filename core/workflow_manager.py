"""Deterministic, branch-specific remediation workflows."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from config.agent_config import DEFAULT_DEPARTMENT_ROUTING


@dataclass
class WorkflowResult:
    workflow_name: str
    department: str
    steps: list[str] = field(default_factory=list)
    business_actions: list[dict] = field(default_factory=list)
    requires_human_review: bool = False
    processing_time_seconds: float = 0.0


_WORKFLOW_NAMES = {
    "Complaint": "Complaint remediation",
    "General Enquiry": "Enquiry resolution",
    "Service Request": "Service fulfilment",
    "Escalation": "Escalation management",
}


def _route_department(category: str, urgency: str) -> str:
    if category == "Escalation" or urgency == "Critical":
        return "Senior Manager"
    return DEFAULT_DEPARTMENT_ROUTING.get(category, "Customer Support")


def _action(action: str, status: str = "Completed") -> dict[str, str]:
    return {"action": action, "status": status}


def execute_workflow(category: str, urgency: str, confidence: float,
                     confidence_threshold: float, gemini_department: str | None = None) -> WorkflowResult:
    """Apply the auditable remediation plan selected by classification."""
    start = time.perf_counter()
    is_critical = category == "Escalation" or urgency == "Critical"
    requires_review = is_critical or confidence < confidence_threshold
    department = _route_department(category, urgency) if is_critical else (
        gemini_department or _route_department(category, urgency)
    )
    plans = {
        "Complaint": [
            _action("Acknowledge complaint"), _action(f"Assign priority case to {department}"),
            _action("Set two-hour follow-up reminder"), _action("Create priority case log"),
        ],
        "General Enquiry": [
            _action("Classify enquiry sub-topic"), _action("Generate knowledge-based response"),
            _action("Send response", "Pending customer delivery"), _action("Log as resolved"),
        ],
        "Service Request": [
            _action("Validate required service details"), _action(f"Route request to {department}"),
            _action("Generate service confirmation"), _action("Start service-level agreement timer"),
        ],
        "Escalation": [
            _action("Flag for immediate human review"), _action("Notify senior manager"),
            _action("Draft urgent acknowledgement"), _action("Pause automatic resolution"),
        ],
    }
    actions = plans.get(category, plans["General Enquiry"])
    steps = ["Request received", "Request classified", "Urgency assessed", "Entities extracted"]
    steps.extend(action["action"] for action in actions)
    if requires_review and not is_critical:
        actions.append(_action("Flag for human review"))
        steps.append("Flagged for human review")
    steps.append("Audit record updated")
    return WorkflowResult(
        workflow_name=_WORKFLOW_NAMES.get(category, "Enquiry resolution"),
        department=department,
        steps=steps,
        business_actions=actions,
        requires_human_review=requires_review,
        processing_time_seconds=round(time.perf_counter() - start, 4),
    )
