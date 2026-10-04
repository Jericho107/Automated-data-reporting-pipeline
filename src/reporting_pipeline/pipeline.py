from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from .core import REQUIRED_COLUMNS, parse_csv, reconcile, validate_rows


def parse_json_records(text: str) -> list[dict[str, str]]:
    payload = json.loads(text)
    if not isinstance(payload, list):
        raise ValueError("JSON source must be a list of records")
    rows: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict) or tuple(item.keys()) != REQUIRED_COLUMNS:
            raise ValueError("JSON schema drift")
        rows.append({key: str(item[key]) for key in REQUIRED_COLUMNS})
    validate_rows(rows)
    return rows


def merge_sources(*sources: list[dict[str, str]]) -> list[dict[str, str]]:
    merged = [row for source in sources for row in source]
    validate_rows(merged)
    return merged


def _run_id(rows: list[dict[str, str]]) -> str:
    return sha256(reconcile(rows).checksum.encode("utf-8")).hexdigest()[:16]


def run_pipeline(
    csv_text: str,
    json_text: str,
    database_path: str | Path,
) -> dict[str, object]:
    csv_rows = parse_csv(csv_text)
    json_rows = parse_json_records(json_text)
    rows = merge_sources(csv_rows, json_rows)
    source = reconcile(rows)
    run_id = _run_id(rows)

    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS raw_reporting(
                record_id TEXT PRIMARY KEY,
                period TEXT NOT NULL,
                entity TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0)
            );
            CREATE TABLE IF NOT EXISTS pipeline_runs(
                run_id TEXT PRIMARY KEY,
                source_rows INTEGER NOT NULL,
                source_total REAL NOT NULL,
                source_checksum TEXT NOT NULL,
                status TEXT NOT NULL
            );
            """
        )
        connection.executemany(
            """
            INSERT INTO raw_reporting(record_id, period, entity, amount)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(record_id) DO UPDATE SET
                period=excluded.period,
                entity=excluded.entity,
                amount=excluded.amount
            """,
            [
                (row["record_id"], row["period"], row["entity"], float(row["amount"]))
                for row in rows
            ],
        )

        target_rows = [
            {
                "record_id": str(record_id),
                "period": str(period),
                "entity": str(entity),
                "amount": f"{float(amount):.2f}",
            }
            for record_id, period, entity, amount in connection.execute(
                "SELECT record_id, period, entity, amount FROM raw_reporting ORDER BY record_id"
            ).fetchall()
            if record_id in {row["record_id"] for row in rows}
        ]
        target = reconcile(target_rows)
        status = "PASS" if source == target else "FAIL"
        connection.execute(
            """
            INSERT INTO pipeline_runs VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET status=excluded.status
            """,
            (run_id, source.rows, source.total_amount, source.checksum, status),
        )
        connection.commit()

        if status != "PASS":
            raise ValueError("source-to-target reconciliation failed")

        by_entity = {
            entity: round(total, 2)
            for entity, total in connection.execute(
                """
                SELECT entity, SUM(amount)
                FROM raw_reporting
                WHERE record_id IN ({})
                GROUP BY entity
                ORDER BY entity
                """.format(",".join("?" for _ in rows)),
                [row["record_id"] for row in rows],
            ).fetchall()
        }
        return {
            "run_id": run_id,
            "sources": {"csv_rows": len(csv_rows), "json_rows": len(json_rows)},
            "reconciliation": asdict(source),
            "status": status,
            "entity_totals": by_entity,
        }
    finally:
        connection.close()


def sample_json() -> str:
    return json.dumps(
        [
            {"record_id": "R004", "period": "2026-09", "entity": "C", "amount": "500.00"},
            {"record_id": "R005", "period": "2026-09", "entity": "B", "amount": "275.50"},
        ]
    )
