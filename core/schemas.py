"""
Pydantic schemas that validate the JSON returned by Gemini before it is
ever trusted by the workflow manager or written to the database.

This is the "JSON Validation" step in the architecture diagram: Gemini's
raw text response is parsed and checked here. If validation fails, the
caller (gemini_client.py) raises SchemaValidationError, which the UI
surfaces as an explicit error rather than silently trusting bad data.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from config.agent_config import CATEGORIES, URGENCY_LEVELS


class Entities(BaseModel):
    issue: Optional[str] = ""
    product: Optional[str] = ""
    amount: Optional[str] = ""

    class Config:
        extra = "allow"  # Gemini may return additional entity keys; keep them


class RequestAnalysis(BaseModel):
    """Schema for a single-request Gemini analysis."""

    category: str
    urgency: str
    department: str
    confidence: float = Field(ge=0.0, le=1.0)
    entities: Entities = Field(default_factory=Entities)
    draft_response: str
    reason: str

    @field_validator("category")
    @classmethod
    def _check_category(cls, v: str) -> str:
        if v not in CATEGORIES:
            raise ValueError(f"category must be one of {CATEGORIES}, got '{v}'")
        return v

    @field_validator("urgency")
    @classmethod
    def _check_urgency(cls, v: str) -> str:
        if v not in URGENCY_LEVELS:
            raise ValueError(f"urgency must be one of {URGENCY_LEVELS}, got '{v}'")
        return v


class BatchRequestAnalysis(RequestAnalysis):
    """Schema for one item inside a batch Gemini response."""

    request_id: str
    customer_name: Optional[str] = ""


class SchemaValidationError(Exception):
    """Raised when Gemini's response fails schema validation."""
