"""
Thin wrapper around google-generativeai. This is the only module that
talks to the Gemini API directly, so retries, JSON cleanup, and schema
validation all live in one place.
"""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

import google.generativeai as genai
from pydantic import ValidationError

from config.agent_config import GeminiConfig
from core.schemas import BatchRequestAnalysis, RequestAnalysis, SchemaValidationError

logger = logging.getLogger("firstsource_poc")

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class GeminiClientError(Exception):
    """Raised for any unrecoverable Gemini call/parse failure."""


def _clean_json_text(text: str) -> str:
    """Extract the first complete JSON object or array from a model response."""
    cleaned = _CODE_FENCE_RE.sub("", text).strip()
    first_brace = min(
        (index for index in (cleaned.find("{"), cleaned.find("[")) if index != -1),
        default=-1,
    )
    if first_brace == -1:
        return cleaned

    candidate = cleaned[first_brace:]
    try:
        _, end_index = json.JSONDecoder().raw_decode(candidate)
    except json.JSONDecodeError:
        # Return the candidate so the caller can include a useful error and retry.
        return candidate
    return candidate[:end_index]


def _call_gemini(prompt: str, config: GeminiConfig, retries: int = 1) -> str:
    if not config.api_key:
        raise GeminiClientError(
            "GEMINI_API_KEY is not set. Add it to your .env file or "
            "Streamlit secrets before analysing requests."
        )

    genai.configure(api_key=config.api_key)
    model = genai.GenerativeModel(
        model_name=config.model,
        generation_config={
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_output_tokens": config.max_output_tokens,
            "response_mime_type": "application/json",
        },
    )

    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            response = model.generate_content(prompt, request_options={"timeout": 30})
            return response.text
        except Exception as exc:  # noqa: BLE001 - surfaced to caller
            last_error = exc
            logger.warning("Gemini call failed (attempt %s/%s): %s", attempt, retries + 1, exc)
            # A short retry handles transient rate/network errors without making
            # an interactive Streamlit request appear frozen.
            time.sleep(min(0.5 * (2 ** (attempt - 1)), 1.0))

    raise GeminiClientError(f"Gemini API call failed after retries: {last_error}") from last_error


def analyse_single_request(
    customer_name: str,
    customer_email: str,
    request_text: str,
    config: GeminiConfig,
    prompt_builder,
) -> RequestAnalysis:
    """Analyse one customer request end-to-end: call Gemini, parse, validate."""
    prompt = prompt_builder(customer_name, customer_email, request_text)
    data = _call_and_parse_json(prompt, config, expected_type=dict, description="JSON object")

    try:
        return RequestAnalysis.model_validate(data)
    except ValidationError as exc:
        raise SchemaValidationError(f"Gemini JSON failed schema validation: {exc}") from exc


def analyse_batch(
    emails: list[dict],
    config: GeminiConfig,
    prompt_builder,
) -> list[BatchRequestAnalysis]:
    """Analyse a batch, splitting it automatically if its response is too large."""
    try:
        prompt = prompt_builder(emails)
        data = _call_and_parse_json(prompt, config, expected_type=list, description="JSON array")

        expected_request_ids = {email["request_id"] for email in emails}
        returned_request_ids = {
            item.get("request_id") for item in data if isinstance(item, dict)
        }
        if returned_request_ids != expected_request_ids:
            raise SchemaValidationError(
                "Gemini returned an incomplete batch response; retrying with smaller batches."
            )

        results = []
        for item in data:
            try:
                results.append(BatchRequestAnalysis.model_validate(item))
            except ValidationError as exc:
                raise SchemaValidationError(
                    "Gemini returned an invalid batch item; retrying with smaller batches."
                ) from exc
        return results
    except (GeminiClientError, SchemaValidationError) as exc:
        if len(emails) == 1:
            raise

        midpoint = len(emails) // 2
        logger.warning(
            "Batch of %s emails failed (%s). Splitting it into batches of %s and %s.",
            len(emails),
            exc,
            midpoint,
            len(emails) - midpoint,
        )
        return (
            analyse_batch(emails[:midpoint], config, prompt_builder)
            + analyse_batch(emails[midpoint:], config, prompt_builder)
        )


def _call_and_parse_json(
    prompt: str,
    config: GeminiConfig,
    *,
    expected_type: type,
    description: str,
    parse_retries: int = 1,
) -> Any:
    """Request structured output again when the model returns incomplete JSON."""
    last_error: json.JSONDecodeError | None = None
    raw_text = ""

    for _ in range(parse_retries + 1):
        raw_text = _call_gemini(prompt, config)
        try:
            data = json.loads(_clean_json_text(raw_text))
        except json.JSONDecodeError as exc:
            last_error = exc
            logger.warning("Gemini returned malformed %s; retrying: %s", description, exc)
            continue

        if not isinstance(data, expected_type):
            raise SchemaValidationError(f"Expected a {description} from Gemini.")
        return data

    raise GeminiClientError(
        f"Gemini did not return valid {description} after {parse_retries + 1} attempts: "
        f"{last_error}\nRaw: {raw_text[:500]}"
    ) from last_error
