from __future__ import annotations

from html import escape
from pathlib import Path

from .core import sample_csv
from .pipeline import run_pipeline, sample_json


def render_delivery(result: dict[str, object]) -> str:
    rows = "".join(
        f"<tr><td>{escape(entity)}</td><td>{amount:.2f}</td></tr>"
        for entity, amount in result["entity_totals"].items()
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Automated Reporting Delivery</title></head>
<body>
<h1>Automated Reporting Delivery</h1>
<p><strong>Run:</strong> {escape(str(result["run_id"]))}</p>
<p><strong>Status:</strong> {escape(str(result["status"]))}</p>
<p><strong>Rows:</strong> {result["reconciliation"]["rows"]}</p>
<p><strong>Total:</strong> {result["reconciliation"]["total_amount"]:.2f}</p>
<h2>Entity totals</h2>
<table><thead><tr><th>Entity</th><th>Amount</th></tr></thead><tbody>{rows}</tbody></table>
<p><small>Synthetic recurring-reporting demonstration.</small></p>
</body></html>"""


def build_delivery(database_path: str | Path) -> tuple[dict[str, object], str]:
    result = run_pipeline(sample_csv(), sample_json(), database_path)
    return result, render_delivery(result)


def write_rendered_delivery(
    result: dict[str, object],
    output_path: str | Path,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_delivery(result), encoding="utf-8")
    return output


def write_delivery(database_path: str | Path, output_path: str | Path) -> Path:
    result, _ = build_delivery(database_path)
    return write_rendered_delivery(result, output_path)
