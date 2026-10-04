from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

from .core import parse_csv, sample_csv, serialise_sample
from .delivery import write_delivery
from .pipeline import run_pipeline, sample_json


def smoke() -> int:
    payload = serialise_sample()
    payload["multi_source"] = run_pipeline(sample_csv(), sample_json(), ":memory:")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def deliver() -> int:
    path = write_delivery("output/reporting.sqlite", "output/management_report.html")
    print(path.as_posix())
    return 0


def reverse_test() -> int:
    cases: list[dict[str, str]] = []
    corruptions = [
        ("schema-drift", "record_id,period,entity,total\nR1,2026-09,A,10\n"),
        ("duplicate-id", "record_id,period,entity,amount\nR1,2026-09,A,10\nR1,2026-09,B,20\n"),
    ]
    for name, payload in corruptions:
        try:
            parse_csv(payload)
        except ValueError as exc:
            cases.append({"case": name, "status": "PASS", "error": str(exc)})
        else:
            cases.append({"case": name, "status": "FAIL", "error": "corruption accepted"})

    path = Path("output/reverse_reporting.sqlite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    result = run_pipeline(sample_csv(), sample_json(), path)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE raw_reporting SET entity='CORRUPTED' WHERE record_id='R001'")
        connection.commit()
        row = connection.execute(
            "SELECT entity FROM raw_reporting WHERE record_id='R001'"
        ).fetchone()
    cases.append(
        {
            "case": "target-non-financial-mutation",
            "status": "PASS" if result["status"] == "PASS" and row[0] == "CORRUPTED" else "FAIL",
            "error": "mutation created for reconciliation test",
        }
    )

    rerun = run_pipeline(sample_csv(), sample_json(), path)
    with sqlite3.connect(path) as connection:
        restored = connection.execute(
            "SELECT entity FROM raw_reporting WHERE record_id='R001'"
        ).fetchone()[0]
        run_count = connection.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0]
    cases.append(
        {
            "case": "idempotent-recovery",
            "status": "PASS" if rerun["status"] == "PASS" and restored == "A" and run_count == 1 else "FAIL",
            "error": "same run restores source state without duplicate run manifest",
        }
    )

    print(json.dumps(cases, indent=2, sort_keys=True))
    return 0 if all(case["status"] == "PASS" for case in cases) else 1


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if command == "smoke":
        return smoke()
    if command == "deliver":
        return deliver()
    if command == "reverse-test":
        return reverse_test()
    print("usage: python -m reporting_pipeline.cli [smoke|deliver|reverse-test]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
