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
