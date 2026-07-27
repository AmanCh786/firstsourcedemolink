"""
Central configuration for the Incoming Request Processing Workflow POC.

All tunables live here (or are overridden via environment variables / .env)
so the rest of the codebase never hard-codes a model name, threshold, or
batch size. This is what the "Configuration" page in the Streamlit app
reads and displays.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()  # loads .env if present; safe no-op otherwise


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _get_float(name: str, default: float) -> float:
    val = os.getenv(name)
    try:
        return float(val) if val is not None else default
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    val = os.getenv(name)
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default


CATEGORIES = ["Complaint", "General Enquiry", "Service Request", "Escalation"]
URGENCY_LEVELS = ["Low", "Medium", "High", "Critical"]

# Default department routing per category. WorkflowManager can still
# override this using entities/urgency (e.g. Escalation -> Senior Manager).
DEFAULT_DEPARTMENT_ROUTING = {
    "Complaint": "Billing Team",
    "General Enquiry": "Customer Support",
    "Service Request": "Operations Team",
    "Escalation": "Senior Manager",
}


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    temperature: float = field(default_factory=lambda: _get_float("GEMINI_TEMPERATURE", 0.2))
    top_p: float = field(default_factory=lambda: _get_float("GEMINI_TOP_P", 0.95))
    max_output_tokens: int = field(default_factory=lambda: _get_int("GEMINI_MAX_TOKENS", 8192))
    confidence_threshold: float = field(default_factory=lambda: _get_float("CONFIDENCE_THRESHOLD", 0.80))


@dataclass(frozen=True)
class BatchConfig:
    enable_batch_processing: bool = field(default_factory=lambda: _get_bool("ENABLE_BATCH_PROCESSING", True))
    batch_size: int = field(default_factory=lambda: _get_int("BATCH_SIZE", 20))
    max_parallel_workers: int = field(default_factory=lambda: _get_int("MAX_PARALLEL_WORKERS", 5))
    max_batch_requests: int = field(default_factory=lambda: _get_int("MAX_BATCH_REQUESTS", 100))


GEMINI_CONFIG = GeminiConfig()
BATCH_CONFIG = BatchConfig()
DB_PATH = os.getenv("DB_PATH", "data/requests.db")

# Sample requests used by the "Example Requests" quick-fill buttons on Home.
SAMPLE_REQUESTS = {
    "Complaint": (
        "I was charged twice for my broadband bill this month. "
        "Please refund the extra payment immediately, this is unacceptable."
    ),
    "General Enquiry": (
        "Hi, I wanted to know what broadband plans you currently offer for "
        "a 2-person household and whether there is a student discount."
    ),
    "Service Request": (
        "I recently moved to a new apartment and would like to request a "
        "new broadband connection installation at my new address."
    ),
    "Escalation": (
        "This is the third time I am writing about the same billing issue "
        "with no resolution in two weeks. I want this escalated to a manager "
        "immediately or I will cancel my subscription."
    ),
}
