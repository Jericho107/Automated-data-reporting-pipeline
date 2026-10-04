from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_power_query_asset_has_explicit_file_parameter_and_contract():
    text = (ROOT / "powerquery" / "clean_reporting_source.m").read_text(encoding="utf-8")

    assert "File.Contents(pSourcePath)" in text
    assert "MissingField.Error" in text
    assert 'Item="Raw_Transactions"' in text
    assert 'Item="Entity_Map"' in text
    assert "Table.NestedJoin" in text
    assert "try Number.FromText" in text
    assert '"Canonical Entity"' in text
    assert "Table.Distinct" in text


def test_power_query_documentation_keeps_runtime_claim_boundary():
    text = (ROOT / "powerquery" / "README.md").read_text(encoding="utf-8").lower()

    assert "does **not** claim power query desktop runtime validation" in text
