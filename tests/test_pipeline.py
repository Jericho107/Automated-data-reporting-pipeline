import sqlite3

import pytest

from reporting_pipeline.core import sample_csv
from reporting_pipeline.pipeline import merge_sources, parse_json_records, run_pipeline, sample_json


def test_multi_source_run_reconciles_and_is_idempotent(tmp_path):
    path = tmp_path / "reporting.sqlite"
    first = run_pipeline(sample_csv(), sample_json(), path)
    second = run_pipeline(sample_csv(), sample_json(), path)

    assert first == second
    assert first["status"] == "PASS"
    assert first["sources"] == {"csv_rows": 3, "json_rows": 2}

    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM raw_reporting").fetchone()[0] == 5
        assert connection.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0] == 1
        assert connection.execute(
            "SELECT execution_count FROM pipeline_runs"
        ).fetchone()[0] == 2


def test_duplicate_key_across_sources_is_rejected():
    duplicate_json = '[{"record_id":"R001","period":"2026-09","entity":"X","amount":"1.00"}]'
    with pytest.raises(ValueError, match="duplicate record_id"):
        merge_sources(
            __import__("reporting_pipeline.core", fromlist=["parse_csv"]).parse_csv(sample_csv()),
            parse_json_records(duplicate_json),
        )


def test_json_schema_drift_is_rejected():
    with pytest.raises(ValueError, match="JSON schema drift"):
        parse_json_records('[{"record_id":"R9","period":"2026-09","amount":"1.00"}]')


def test_smaller_next_snapshot_removes_stale_target_records(tmp_path):
    path = tmp_path / "reporting.sqlite"
    run_pipeline(sample_csv(), sample_json(), path)
    reduced_json = (
        '[{"record_id":"R004","period":"2026-09","entity":"C","amount":"500.00"}]'
    )

    result = run_pipeline(sample_csv(), reduced_json, path)

    assert result["reconciliation"]["rows"] == 4
    with sqlite3.connect(path) as connection:
        ids = {
            row[0]
            for row in connection.execute(
                "SELECT record_id FROM raw_reporting ORDER BY record_id"
            ).fetchall()
        }
        assert ids == {"R001", "R002", "R003", "R004"}
        assert connection.execute(
            "SELECT COUNT(*) FROM pipeline_runs"
        ).fetchone()[0] == 2


def test_invalid_next_source_preserves_last_good_snapshot(tmp_path):
    path = tmp_path / "reporting.sqlite"
    run_pipeline(sample_csv(), sample_json(), path)
    invalid_json = (
        '[{"record_id":"R001","period":"2026-09","entity":"X","amount":"1.00"}]'
    )

    with pytest.raises(ValueError, match="duplicate record_id"):
        run_pipeline(sample_csv(), invalid_json, path)

    with sqlite3.connect(path) as connection:
        rows = connection.execute(
            "SELECT record_id, entity, amount FROM raw_reporting ORDER BY record_id"
        ).fetchall()

    assert rows == [
        ("R001", "A", 1200.5),
        ("R002", "B", 840.25),
        ("R003", "A", 315.0),
        ("R004", "C", 500.0),
        ("R005", "B", 275.5),
    ]
