from pathlib import Path

from reporting_pipeline.core import sample_csv
from reporting_pipeline.pipeline import run_pipeline, sample_json

ROOT = Path(__file__).resolve().parents[1]


def _sql(name: str) -> str:
    return (ROOT / "sql" / name).read_text(encoding="utf-8")


def test_management_summary_sql_executes(tmp_path):
    path = tmp_path / "reporting.sqlite"
    run_pipeline(sample_csv(), sample_json(), path)

    import sqlite3

    with sqlite3.connect(path) as connection:
        rows = connection.execute(_sql("10_management_summary.sql")).fetchall()

    assert rows
    assert {row[1] for row in rows} == {"A", "B", "C"}


def test_run_control_and_reconciliation_sql_execute(tmp_path):
    path = tmp_path / "reporting.sqlite"
    run_pipeline(sample_csv(), sample_json(), path)

    import sqlite3

    with sqlite3.connect(path) as connection:
        runs = connection.execute(_sql("20_run_control.sql")).fetchall()
        recon = connection.execute(_sql("30_target_reconciliation.sql")).fetchall()

    assert len(runs) == 1
    assert len(recon) == 1
    assert recon[0][-1] == "PASS"


def test_reconciliation_sql_tracks_latest_snapshot_after_source_change(tmp_path):
    path = tmp_path / "reporting.sqlite"
    run_pipeline(sample_csv(), sample_json(), path)
    reduced_json = (
        '[{"record_id":"R004","period":"2026-09","entity":"C","amount":"500.00"}]'
    )
    run_pipeline(sample_csv(), reduced_json, path)

    import sqlite3

    with sqlite3.connect(path) as connection:
        recon = connection.execute(_sql("30_target_reconciliation.sql")).fetchone()

    assert recon is not None
    assert recon[1] == 4
    assert recon[2] == 4
    assert recon[-1] == "PASS"
