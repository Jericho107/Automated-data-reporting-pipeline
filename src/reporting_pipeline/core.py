from __future__ import annotations

import csv
import hashlib
import io
import sqlite3
from collections.abc import Iterable
from dataclasses import asdict, dataclass

REQUIRED_COLUMNS = ("record_id", "period", "entity", "amount")


@dataclass(frozen=True)
class ReconciliationResult:
    rows: int
    total_amount: float
    checksum: str


def parse_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    if tuple(reader.fieldnames or ()) != REQUIRED_COLUMNS:
        raise ValueError(
            f"schema drift: expected {REQUIRED_COLUMNS}, got {reader.fieldnames}"
        )
    rows = list(reader)
    validate_rows(rows)
    return rows


def validate_rows(rows: Iterable[dict[str, str]]) -> None:
    seen: set[str] = set()
    for row in rows:
        record_id = row["record_id"].strip()
        if not record_id:
            raise ValueError("record_id is required")
        if record_id in seen:
            raise ValueError(f"duplicate record_id: {record_id}")
        seen.add(record_id)
        if not row["period"].strip() or not row["entity"].strip():
            raise ValueError("period and entity are required")
        try:
            amount = float(row["amount"])
        except ValueError as exc:
            raise ValueError("amount must be numeric") from exc
        if amount < 0:
            raise ValueError("amount must be non-negative")


def reconcile(rows: list[dict[str, str]]) -> ReconciliationResult:
    canonical = "\n".join(
        "|".join(row[key].strip() for key in REQUIRED_COLUMNS)
        for row in sorted(rows, key=lambda item: item["record_id"])
    )
    return ReconciliationResult(
        rows=len(rows),
        total_amount=round(sum(float(row["amount"]) for row in rows), 2),
        checksum=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )


def load_sqlite(
    rows: list[dict[str, str]],
    path: str = ":memory:",
) -> ReconciliationResult:
    conn = sqlite3.connect(path)
    try:
        conn.execute("DROP TABLE IF EXISTS raw_reporting")
        conn.execute(
            "CREATE TABLE raw_reporting("
            "record_id TEXT PRIMARY KEY, period TEXT NOT NULL, "
            "entity TEXT NOT NULL, amount REAL NOT NULL CHECK(amount >= 0))"
        )
        conn.executemany(
            "INSERT INTO raw_reporting VALUES(?,?,?,?)",
            [
                (
                    row["record_id"],
                    row["period"],
                    row["entity"],
                    float(row["amount"]),
                )
                for row in rows
            ],
        )
        target = [
            {
                "record_id": str(record_id),
                "period": str(period),
                "entity": str(entity),
                "amount": f"{float(amount):.2f}",
            }
            for record_id, period, entity, amount in conn.execute(
                "SELECT record_id, period, entity, amount FROM raw_reporting ORDER BY record_id"
            ).fetchall()
        ]
        source = reconcile(rows)
        target_result = reconcile(target)
        if (
            target_result.rows != source.rows
            or target_result.total_amount != source.total_amount
            or target_result.checksum != source.checksum
        ):
            raise ValueError("source-to-target reconciliation failed")
        return target_result
    finally:
        conn.close()


def sample_csv() -> str:
    return (
        "record_id,period,entity,amount\n"
        "R001,2026-09,A,1200.50\n"
        "R002,2026-09,B,840.25\n"
        "R003,2026-09,A,315.00\n"
    )


def serialise_sample() -> dict[str, object]:
    rows = parse_csv(sample_csv())
    source = reconcile(rows)
    target = load_sqlite(rows)
    return {
        "source": asdict(source),
        "target": asdict(target),
        "reconciled": source == target,
    }
