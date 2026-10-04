<div align="center">

# Automated Data Reporting Pipeline

### Excel · Power Query · Multi-source ingestion · SQL · Reconciliation · Management delivery

**Python 3.12 · openpyxl · Power Query M · SQL/SQLite · Docker · GitHub Actions**

**Pretoria BI — Data · Intelligence · Performance**

</div>

---

## Executive question

> **Can recurring management reporting survive messy Excel inputs, source-system variation and reruns without silently changing the numbers?**

This repository is a controlled reporting system, not a formatting exercise. It demonstrates how Pretoria BI can take spreadsheet-heavy operational reporting and turn it into a reproducible, auditable delivery chain.

## What the case proves

| Layer | Executable evidence |
|---|---|
| Excel source | deterministic multi-sheet workbook with deliberate business-data defects |
| Data quality | schema, key, mapping, period, amount and reportable-status controls |
| Power Query | version-controlled M transformation with explicit source parameter and schema contract |
| Python | reference transformation and workbook generation |
| SQL | executable landing, management summary, run control and reconciliation queries |
| Multi-source | CSV + JSON/API-shaped ingestion with cross-source key control |
| Reconciliation | row, amount and canonical full-row checksum controls |
| Idempotency | same source state restores target state without duplicate run manifests |
| Delivery | HTML report + controlled Excel management pack |
| Operations | auditable run manifest with artefact SHA-256 fingerprints |
| Scheduling | recurring GitHub Actions execution + manual dispatch |
| Portability | Docker image built and executed in CI |
| CI | compile, Ruff, tests, smoke, delivery, Excel generation, container run and reverse tests |

## Excel case study

Run:

```bash
python -m reporting_pipeline.cli excel-demo
```

The command generates:

```text
output/
├── source_messy_reporting.xlsx
├── clean_management_report.xlsx
└── excel_evidence.json
```

### Source workbook — intentionally messy

`source_messy_reporting.xlsx` contains three worksheets:

- **Raw_Transactions** — mixed casing, European currency strings, duplicate key, negative value, missing period, unmapped entity, invalid numeric value and a non-reportable status;
- **Entity_Map** — controlled raw-to-canonical business mapping;
- **Parameters** — reporting period, required status, currency, owner and fail-closed mode.

The defects are deterministic test fixtures. Nothing is silently “cleaned away.”

### Management workbook

`clean_management_report.xlsx` contains:

- **Executive_Summary** — control KPIs and entity-level accepted value;
- **Clean_Data** — accepted, typed, canonical records with source-row lineage;
- **Data_Quality_Log** — rejected/flagged rows with rule, severity, field and source value;
- **Reconciliation** — explicit control totals and PASS/FAIL status;
- **Parameters** — evidence metadata and transformation boundary.

The workbook includes a management chart, Excel table semantics, frozen panes, number formats and conditional formatting. The purpose is not decorative Excel: it is to make the control chain inspectable by an analyst or manager.

## Power Query evidence

`powerquery/clean_reporting_source.m` is the version-controlled Power Query transformation. It uses a text parameter named `pSourcePath`, opens the workbook with `Excel.Workbook(File.Contents(...))`, enforces the expected columns with `MissingField.Error`, normalises text and locale-dependent amounts, applies types and controls the reportable population.

**Evidence boundary:** the M code is present and reviewable, but this repository does not claim Microsoft Excel/Power Query Desktop runtime validation until a Desktop execution artefact is captured. CI validates the executable Python/openpyxl reference path.

See `docs/excel_power_query_validation.md`.

## End-to-end control plane

```text
MESSY EXCEL ──────────────┐
CSV SOURCE ───────────────┼──> CONTRACTS / DQ / KEY CONTROL
JSON / API-SHAPED SOURCE ─┘              │
                                         v
                               CANONICAL SOURCE STATE
                                         │
                       ┌─────────────────┴─────────────────┐
                       v                                   v
              SQLITE CONTROL LAYER                 EXCEL CONTROL PACK
                       │                                   │
                       v                                   v
            FULL-ROW RECONCILIATION              DQ LOG + RECONCILIATION
                       │                                   │
                       └─────────────────┬─────────────────┘
                                         v
                               MANAGEMENT DELIVERY
```

## Operational run

```bash
python -m reporting_pipeline.cli operate
```

This produces one inspectable evidence bundle under `output/operational/` containing the
SQLite target, HTML management report, messy source workbook, controlled Excel report and
`run_manifest.json`. The manifest records the run identity, source/target control totals,
SQL reconciliation result, Excel DQ outcome and SHA-256 fingerprint of every delivered
artefact.

The target is published as a transactional **current snapshot**. A smaller subsequent source
must remove stale target records; an invalid next source must leave the last valid snapshot
unchanged. Both behaviors are reverse-tested.

## Recurring execution

`.github/workflows/scheduled-reporting.yml` runs the quality gate and operational reporting
chain every Monday and also supports manual dispatch. The resulting evidence bundle is stored
as a GitHub Actions artefact with a defined retention period.

This proves recurring automation in GitHub Actions. It is not presented as enterprise
orchestration or SLA monitoring.

## Container runtime

```bash
docker build -t automated-reporting-pipeline .
docker run --rm automated-reporting-pipeline
```

The main CI workflow builds the image, executes the reporting pipeline inside the container
and asserts that the operational manifest was produced.

## Reverse testing

The repository deliberately attacks its own assumptions.

Current failure injections cover:

1. CSV schema drift;
2. duplicate business keys;
3. target non-financial mutation;
4. idempotent recovery after target corruption;
5. Excel schema drift;
6. duplicate Excel business key;
7. missing reporting period;
8. unmapped business entity;
9. invalid/negative amount;
10. non-reportable status.

A reporting repository should not receive proof credit merely because the happy path runs.

## Run locally

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m reporting_pipeline.cli smoke
python -m reporting_pipeline.cli deliver
python -m reporting_pipeline.cli excel-demo
python -m reporting_pipeline.cli operate
python -m reporting_pipeline.cli reverse-test
```

GitHub Actions publishes the generated reporting evidence bundle as a workflow artefact.

## Scope and limitations

All data are synthetic. This project demonstrates controlled reporting architecture and spreadsheet automation patterns. It does **not** claim:

- a live client integration;
- enterprise orchestration, retry queues or SLA monitoring;
- enterprise authentication or secret management;
- Microsoft Excel/Power Query Desktop runtime validation;
- measured client ROI;
- production-scale volume or SLA evidence.

Those boundaries are intentional. Claims in this repository are limited to evidence that can be inspected or executed.

---

**Pretoria BI — Understand · Decide · Act · Measure**
