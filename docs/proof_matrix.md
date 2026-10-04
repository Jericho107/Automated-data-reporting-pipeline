# Validation Matrix

| Claim | Executable evidence | Failure path | Status |
|---|---|---|---|
| CSV schema is explicit | `core.parse_csv` | renamed/missing column | implemented |
| JSON/API-style schema is explicit | `pipeline.parse_json_records` | missing/extra JSON field | implemented |
| Business keys are unique across all sources | `pipeline.merge_sources` | duplicate key across CSV + JSON | implemented |
| Source state is canonical and deterministic | SHA-256 reconciliation | non-financial field mutation | implemented |
| Target load is idempotent | SQLite upsert + deterministic run ID | identical source rerun | implemented |
| Same source state creates one run manifest | `pipeline_runs` primary key | repeated identical run | implemented |
| Target can be restored from source truth | rerun after controlled mutation | target entity mutation | implemented |
| Delivery artefact is generated from reconciled data | `delivery.build_delivery` | CI output-size check | implemented |
| CI validates clean and corrupted states | GitHub Actions + reverse-test CLI | schema, duplicate, mutation/recovery | implemented |
| Production scheduling / authentication | not implemented | not applicable | not claimed |

## Review principle

A recurring report is considered reliable only when its source contract, target state, run identity and delivery artefact can be traced to the same reconciled execution.
