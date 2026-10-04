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


def _ensure_schema(connection: sqlite3.Connection) -> None:
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
            status TEXT NOT NULL CHECK(status IN ('PASS', 'FAIL')),
            execution_count INTEGER NOT NULL DEFAULT 1,
            last_executed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(pipeline_runs)").fetchall()
    }
    if "execution_count" not in columns:
        connection.execute(
            "ALTER TABLE pipeline_runs ADD COLUMN execution_count INTEGER NOT NULL DEFAULT 1"
        )
    if "last_executed_at" not in columns:
        connection.execute("ALTER TABLE pipeline_runs ADD COLUMN last_executed_at TEXT")
        connection.execute(
            "UPDATE pipeline_runs SET last_executed_at = CURRENT_TIMESTAMP "
            "WHERE last_executed_at IS NULL"
        )


def _stage_snapshot(
    connection: sqlite3.Connection,
    rows: list[dict[str, str]],
) -> None:
    connection.execute("DROP TABLE IF EXISTS staging_reporting")
    connection.execute(
        """
        CREATE TEMP TABLE staging_reporting(
            record_id TEXT PRIMARY KEY,
            period TEXT NOT NULL,
            entity TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount >= 0)
        )
        """
    )
    connection.executemany(
        """
        INSERT INTO staging_reporting(record_id, period, entity, amount)
        VALUES (?, ?, ?, ?)
        """,
        [
            (row["record_id"], row["period"], row["entity"], float(row["amount"]))
            for row in rows
        ],
    )


def _read_reconciliation_rows(
    connection: sqlite3.Connection,
    table: str,
) -> list[dict[str, str]]:
    return [
        {
            "record_id": str(record_id),
            "period": str(period),
            "entity": str(entity),
            "amount": f"{float(amount):.2f}",
        }
        for record_id, period, entity, amount in connection.execute(
            f"SELECT record_id, period, entity, amount FROM {table} ORDER BY record_id"
        ).fetchall()
    ]


def publish_snapshot(
    rows: list[dict[str, str]],
    database_path: str | Path,
    sources: dict[str, int],
) -> dict[str, object]:
    validate_rows(rows)
    source = reconcile(rows)
    run_id = _run_id(rows)

    connection = sqlite3.connect(database_path)
    try:
        _ensure_schema(connection)
        _stage_snapshot(connection, rows)

        staged = reconcile(_read_reconciliation_rows(connection, "staging_reporting"))
        if source != staged:
            connection.rollback()
            raise ValueError("source-to-staging reconciliation failed")
        connection.commit()

        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM raw_reporting")
        connection.execute(
            """
            INSERT INTO raw_reporting(record_id, period, entity, amount)
            SELECT record_id, period, entity, amount
            FROM staging_reporting
            """
        )

        target = reconcile(_read_reconciliation_rows(connection, "raw_reporting"))
        status = "PASS" if source == target else "FAIL"
        if status != "PASS":
            connection.rollback()
            raise ValueError("source-to-target reconciliation failed")

        connection.execute(
            """
            INSERT INTO pipeline_runs(
                run_id,
                source_rows,
                source_total,
                source_checksum,
                status,
                execution_count,
                last_executed_at
            )
            VALUES (?, ?, ?, ?, ?, 1, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            ON CONFLICT(run_id) DO UPDATE SET
                status=excluded.status,
                execution_count=pipeline_runs.execution_count + 1,
                last_executed_at=strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            """,
            (run_id, source.rows, source.total_amount, source.checksum, status),
        )
        connection.commit()

        by_entity = {
            entity: round(total, 2)
            for entity, total in connection.execute(
                """
                SELECT entity, SUM(amount)
                FROM raw_reporting
                GROUP BY entity
                ORDER BY entity
                """
            ).fetchall()
        }
        return {
            "run_id": run_id,
            "sources": sources,
            "reconciliation": asdict(source),
            "status": status,
            "entity_totals": by_entity,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def run_pipeline(
    csv_text: str,
    json_text: str,
    database_path: str | Path,
) -> dict[str, object]:
    csv_rows = parse_csv(csv_text)
    json_rows = parse_json_records(json_text)
    rows = merge_sources(csv_rows, json_rows)
    return publish_snapshot(
        rows,
        database_path,
        {"csv_rows": len(csv_rows), "json_rows": len(json_rows)},
    )

def sample_json() -> str:
    return json.dumps(
        [
            {"record_id": "R004", "period": "2026-09", "entity": "C", "amount": "500.00"},
            {"record_id": "R005", "period": "2026-09", "entity": "B", "amount": "275.50"},
        ]
    )
