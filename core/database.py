"""
SQLite persistence layer. Every processed request (single or batch)
lands in one `requests` table, which powers both the Request History
page and the Dashboard KPIs.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator

from config.agent_config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    request_id          TEXT PRIMARY KEY,
    customer_name       TEXT,
    customer_email      TEXT,
    request_text        TEXT,
    category            TEXT,
    urgency             TEXT,
    department          TEXT,
    confidence          REAL,
    entities_json       TEXT,
    draft_response      TEXT,
    reason              TEXT,
    workflow_name       TEXT,
    requires_review     INTEGER,
    status              TEXT,
    processing_time_sec REAL,
    created_at          TEXT,
    source              TEXT
);
"""


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.execute(_SCHEMA)


def insert_request(record: dict[str, Any]) -> None:
    """record must contain all columns in _SCHEMA except created_at (auto-filled)."""
    record = dict(record)
    record.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
    if isinstance(record.get("entities_json"), (dict, list)):
        record["entities_json"] = json.dumps(record["entities_json"])

    columns = [
        "request_id", "customer_name", "customer_email", "request_text",
        "category", "urgency", "department", "confidence", "entities_json",
        "draft_response", "reason", "workflow_name", "requires_review",
        "status", "processing_time_sec", "created_at", "source",
    ]
    placeholders = ", ".join(["?"] * len(columns))
    values = [record.get(col) for col in columns]

    with _connect() as conn:
        conn.execute(
            f"INSERT OR REPLACE INTO requests ({', '.join(columns)}) VALUES ({placeholders})",
            values,
        )


def fetch_all() -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM requests ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def fetch_filtered(
    category: str | None = None,
    urgency: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    query = "SELECT * FROM requests WHERE 1=1"
    params: list[Any] = []
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if urgency and urgency != "All":
        query += " AND urgency = ?"
        params.append(urgency)
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_kpis() -> dict[str, Any]:
    rows = fetch_all()
    total = len(rows)
    if total == 0:
        return {
            "total_requests": 0,
            "by_category": {},
            "by_urgency": {},
            "avg_confidence": 0.0,
            "avg_processing_time": 0.0,
            "human_review_required": 0,
            "successfully_processed": 0,
        }

    by_category: dict[str, int] = {}
    by_urgency: dict[str, int] = {}
    review_count = 0
    conf_sum = 0.0
    time_sum = 0.0

    for r in rows:
        by_category[r["category"]] = by_category.get(r["category"], 0) + 1
        by_urgency[r["urgency"]] = by_urgency.get(r["urgency"], 0) + 1
        review_count += int(r["requires_review"] or 0)
        conf_sum += r["confidence"] or 0.0
        time_sum += r["processing_time_sec"] or 0.0

    return {
        "total_requests": total,
        "by_category": by_category,
        "by_urgency": by_urgency,
        "avg_confidence": round(conf_sum / total, 4),
        "avg_processing_time": round(time_sum / total, 3),
        "human_review_required": review_count,
        "successfully_processed": total - review_count,
    }
