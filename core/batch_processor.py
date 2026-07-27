"""
Batch Manager: optional enhancement on top of the required single-request
workflow. Splits a list of emails into configurable batches and analyses
each batch with one Gemini call, running multiple batches concurrently
with a ThreadPoolExecutor.

  100 Emails -> split into N batches -> ThreadPoolExecutor -> Gemini calls
  -> merge results

This trades a small increase in per-call complexity for fewer total API
calls and lower wall-clock time versus calling Gemini once per email.
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from config.agent_config import BatchConfig, GeminiConfig
from core.gemini_client import GeminiClientError, analyse_batch
from core.prompts import build_batch_prompt
from core.schemas import BatchRequestAnalysis, SchemaValidationError

logger = logging.getLogger("firstsource_poc")


def _chunk(items: list[dict], size: int) -> list[list[dict]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def process_emails_in_batches(
    emails: list[dict],
    gemini_config: GeminiConfig,
    batch_config: BatchConfig,
) -> tuple[list[BatchRequestAnalysis], list[str]]:
    """
    Returns (results, errors). `errors` holds human-readable messages for
    any batch that failed outright, so partial results can still be shown.
    """
    emails = emails[: batch_config.max_batch_requests]
    batches = _chunk(emails, batch_config.batch_size)

    results: list[BatchRequestAnalysis] = []
    errors: list[str] = []

    if not batch_config.enable_batch_processing or len(batches) <= 1:
        # Fall back to sequential single-batch calls if parallelism is off.
        for batch in batches:
            try:
                results.extend(analyse_batch(batch, gemini_config, build_batch_prompt))
            except (GeminiClientError, SchemaValidationError) as exc:
                errors.append(str(exc))
        return results, errors

    with ThreadPoolExecutor(max_workers=batch_config.max_parallel_workers) as executor:
        future_to_batch = {
            executor.submit(analyse_batch, batch, gemini_config, build_batch_prompt): idx
            for idx, batch in enumerate(batches)
        }
        for future in as_completed(future_to_batch):
            idx = future_to_batch[future]
            try:
                results.extend(future.result())
            except (GeminiClientError, SchemaValidationError) as exc:
                logger.error("Batch %s failed: %s", idx, exc)
                errors.append(f"Batch {idx + 1}: {exc}")

    return results, errors


def emails_from_dataframe(df) -> list[dict[str, Any]]:
    """Convert an uploaded CSV (pandas DataFrame) into the email dict shape
    expected by build_batch_prompt / process_emails_in_batches."""
    emails = []
    for i, row in df.iterrows():
        emails.append(
            {
                "request_id": f"REQ{i + 1:05d}",
                "customer_name": str(row.get("Customer", "")).strip(),
                "customer_email": str(row.get("Email", "")).strip(),
                "subject": str(row.get("Subject", "")).strip(),
                "body": str(row.get("Body", "")).strip(),
            }
        )
    return emails
