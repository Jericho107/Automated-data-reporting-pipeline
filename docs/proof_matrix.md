# Validation Matrix

| Claim | Executable evidence | Failure / reverse path | Status |
|---|---|---|---|
| CSV schema is explicit | `core.parse_csv` | renamed/missing column | implemented |
| JSON/API-shaped schema is explicit | `pipeline.parse_json_records` | missing/extra JSON field | implemented |
| Excel source contract is explicit | `excel.transform_excel` | workbook header mutation | implemented |
| Business keys are unique across sources | `pipeline.merge_sources` | duplicate CSV + JSON key | implemented |
| Excel defects are surfaced, not silently discarded | `Data_Quality_Log` + tests | duplicate, missing period, unmapped entity, invalid amount/status | implemented |
| Source state is canonical and deterministic | SHA-256 reconciliation | non-financial field mutation | implemented |
| Published target is an exact current snapshot | staging + atomic snapshot publish | smaller next source must remove stale IDs | implemented |
| Invalid next input preserves last good state | validation before publish | duplicate cross-source key | implemented |
| Same source state is idempotent | deterministic run ID + run metadata | repeated identical run | implemented |
| Repeated execution is auditable | `execution_count`, `last_executed_at` | identical source rerun | implemented |
| SQL reporting layer executes | versioned SQL assets + tests | query execution against generated DB | implemented |
| SQL reconciliation follows latest snapshot | `30_target_reconciliation.sql` | source-state change | implemented |
| Management Excel is generated and reopenable | openpyxl workbook tests | schema/control assertions | implemented |
| Power Query transformation is reviewable | versioned M query | static contract assertions | source-code evidence |
| HTML delivery is generated from reconciled data | `delivery.write_delivery` | CI artefact assertion | implemented |
| Operational evidence is tamper-evident | `run_manifest.json` + SHA-256 artefact hashes | missing/empty artefact fails test | implemented |
| Recurring execution is scheduled | GitHub Actions cron + manual dispatch | scheduled workflow quality gate | implemented |
| Runtime is portable | Docker build + container execution in CI | manifest must exist after container run | implemented |
| CI validates clean and corrupted states | GitHub Actions + reverse-test CLI | multiple injected corruptions | implemented |
| Microsoft Power Query Desktop execution | no Desktop artefact committed | not applicable | not claimed |
| Production SLA / enterprise auth / live client integration | no production evidence | not applicable | not claimed |

## Review principle

A recurring report is reliable only when source contracts, current target state, run identity,
control totals and delivery artefacts can be traced to the same reconciled execution.

Documentation alone is not treated as execution evidence.
