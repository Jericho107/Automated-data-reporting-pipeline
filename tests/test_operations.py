import json

from reporting_pipeline.operations import build_operational_evidence


def test_operational_bundle_is_complete_and_reconciled(tmp_path):
    manifest_path = build_operational_evidence(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["pipeline"]["status"] == "PASS"
    assert manifest["pipeline"]["sql_reconciliation_status"] == "PASS"
    assert manifest["pipeline"]["sources"] == {"excel_rows": 5}
    assert manifest["pipeline"]["source_rows"] == manifest["pipeline"]["target_rows"]
    assert manifest["pipeline"]["source_total"] == manifest["pipeline"]["target_total"]
    assert manifest["excel"]["source_rows"] == 11
    assert manifest["excel"]["accepted_rows"] == 5
    assert manifest["excel"]["rejected_rows"] == 6
    assert manifest["excel"]["accepted_total"] == manifest["pipeline"]["source_total"]
    assert manifest["evidence_boundary"]["power_query_desktop_runtime_validated"] is False

    expected = {
        "reporting.sqlite",
        "management_report.html",
        "source_messy_reporting.xlsx",
        "clean_management_report.xlsx",
    }
    assert set(manifest["artefacts"]) == expected
    assert all(item["bytes"] > 0 for item in manifest["artefacts"].values())
    assert all(len(item["sha256"]) == 64 for item in manifest["artefacts"].values())
