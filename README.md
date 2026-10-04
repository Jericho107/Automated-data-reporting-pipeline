<div align="center">

# Automated Data Reporting Pipeline

### Multi-source ingestion · Contracts · Idempotency · Reconciliation · Delivery

**Python · SQLite · CSV · JSON/API Pattern · CI**

**Pretoria BI — Data · Intelligence · Performance**

</div>

---

## Management question

> **Can a recurring management report be reproduced, reconciled and delivered reliably when its source systems change or a previous load is rerun?**

The project implements a compact reporting control plane rather than a one-off script.

## Pipeline

```text
CSV SOURCE ───────┐
JSON / API ───────┼→ SCHEMA CONTRACT → CROSS-SOURCE KEY CONTROL
                  ↓
          CANONICAL SOURCE STATE
                  ↓
        IDEMPOTENT SQLITE LANDING
                  ↓
      FULL-ROW RECONCILIATION
                  ↓
             RUN MANIFEST
                  ↓
      MANAGEMENT DELIVERY HTML
```

Implemented controls include:

- exact source schema;
- business-key uniqueness inside and across sources;
- canonical SHA-256 checksum;
- row and financial reconciliation;
- non-financial drift detection;
- idempotent upsert behavior;
- deterministic run identifier;
- one manifest row per identical source state;
- generated management delivery artefact.

## Delivery

```bash
python -m reporting_pipeline.cli deliver
```

Produces:

- `output/reporting.sqlite`
- `output/management_report.html`

## Reverse test

The validation path deliberately creates a target mutation, reruns the same source state and proves that:

1. the target is restored to the source state;
2. reconciliation returns to PASS;
3. the same source state does not create duplicate run-manifest records.

## Run locally

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m reporting_pipeline.cli smoke
python -m reporting_pipeline.cli deliver
python -m reporting_pipeline.cli reverse-test
```

All data are synthetic. The implementation demonstrates reporting reliability patterns rather than production scheduling, enterprise authentication or a specific client integration.

---

**Pretoria BI — Understand · Decide · Act · Measure**
