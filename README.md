<div align="center">

# Automated Data Reporting Pipeline

### Contract-driven ingestion, reconciliation, mart generation and delivery evidence for recurring reporting.

**Pretoria BI — Data · Intelligence · Performance**

</div>

---

## Management question

> **Can a recurring report be trusted when source files change or the target load silently diverges?**

**All data and entities are synthetic. No client result or realised ROI is claimed.**

## What this repository proves

- Exact schema contract
- Business-key uniqueness
- Source checksum
- Source/target row and financial reconciliation
- Idempotent SQLite landing pattern

## Evidence chain

```text
SOURCE → CONTRACT → VALIDATION → RECONCILIATION → REPORTING STATE → DELIVERY EVIDENCE
```

## Run locally

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m reporting_pipeline.cli smoke
python -m reporting_pipeline.cli reverse-test
```

## Proof boundary

The repository demonstrates a synthetic technical pattern. It does not claim production scale or realised client impact.

**Pretoria BI — Understand · Decide · Act · Measure**
