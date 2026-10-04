from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .delivery import write_rendered_delivery
from .excel import create_management_workbook, create_messy_source_workbook, transform_excel
from .pipeline import publish_snapshot


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_operational_evidence(output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    database = output / "reporting.sqlite"
    html = output / "management_report.html"
    source_excel = output / "source_messy_reporting.xlsx"
    management_excel = output / "clean_management_report.xlsx"
    manifest_path = output / "run_manifest.json"

    database.unlink(missing_ok=True)
    source_excel.unlink(missing_ok=True)
    management_excel.unlink(missing_ok=True)
    html.unlink(missing_ok=True)
    manifest_path.unlink(missing_ok=True)

    create_messy_source_workbook(source_excel)
    clean_rows, excel_result = transform_excel(source_excel)
    create_management_workbook(source_excel, management_excel)
    pipeline_rows = [
        {
            "record_id": str(row["record_id"]),
            "period": str(row["period"]),
            "entity": str(row["entity"]),
            "amount": f"{float(row['amount']):.2f}",
        }
        for row in clean_rows
    ]
    pipeline_result = publish_snapshot(
        pipeline_rows,
        database,
        {"excel_rows": len(pipeline_rows)},
    )
    write_rendered_delivery(pipeline_result, html)

    sql_candidates = [
        Path.cwd() / "sql",
        Path(__file__).resolve().parents[2] / "sql",
    ]
    sql_root = next((path for path in sql_candidates if path.is_dir()), None)
    if sql_root is None:
        raise RuntimeError("SQL asset directory is unavailable")
    reconciliation_sql = (sql_root / "30_target_reconciliation.sql").read_text(
        encoding="utf-8"
    )

    with sqlite3.connect(database) as connection:
        run = connection.execute(
            """
            SELECT
                run_id,
                source_rows,
                source_total,
                source_checksum,
                status,
                execution_count,
                last_executed_at
            FROM pipeline_runs
            ORDER BY last_executed_at DESC, rowid DESC
            LIMIT 1
            """
        ).fetchone()
        reconciliation = connection.execute(reconciliation_sql).fetchone()
        target_rows = connection.execute(
            "SELECT COUNT(*) FROM raw_reporting"
        ).fetchone()[0]
        target_total = connection.execute(
            "SELECT ROUND(COALESCE(SUM(amount), 0), 2) FROM raw_reporting"
        ).fetchone()[0]

    if run is None or reconciliation is None:
        raise RuntimeError("operational evidence is incomplete")
    if run[4] != "PASS" or reconciliation[-1] != "PASS":
        raise RuntimeError("operational evidence failed reconciliation")

    artefacts = [database, html, source_excel, management_excel]
    manifest: dict[str, Any] = {
        "pipeline": {
            "run_id": run[0],
            "sources": pipeline_result["sources"],
            "source_rows": run[1],
            "source_total": run[2],
            "source_checksum": run[3],
            "status": run[4],
            "execution_count": run[5],
            "last_executed_at": run[6],
            "target_rows": target_rows,
            "target_total": target_total,
            "sql_reconciliation_status": reconciliation[-1],
        },
        "excel": {
            **asdict(excel_result),
            "issues": [asdict(issue) for issue in excel_result.issues],
        },
        "artefacts": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in artefacts
        },
        "evidence_boundary": {
            "synthetic_data": True,
            "power_query_desktop_runtime_validated": False,
            "production_sla_validated": False,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest_path
