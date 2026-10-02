import pytest

from reporting_pipeline.core import load_sqlite, parse_csv, reconcile, sample_csv


def test_reconciliation_is_deterministic() -> None:
    rows = parse_csv(sample_csv())
    assert reconcile(rows) == load_sqlite(rows)
    assert reconcile(rows).total_amount == 2355.75


def test_schema_drift_fails() -> None:
    with pytest.raises(ValueError, match="schema drift"):
        parse_csv("record_id,period,entity,total\nR1,2026-09,A,10\n")


def test_duplicate_id_fails() -> None:
    text = "record_id,period,entity,amount\nR1,2026-09,A,10\nR1,2026-09,B,20\n"
    with pytest.raises(ValueError, match="duplicate record_id"):
        parse_csv(text)
