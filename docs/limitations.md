# Scope and limitations

The repository intentionally separates demonstrated capability from production claims.

## Demonstrated

- Synthetic CSV, JSON/API-shaped and Excel inputs.
- Schema, business-key, mapping, amount and reportable-status controls.
- Power Query M source code for the analyst-facing transformation path.
- Transactional snapshot publishing through a staging table.
- Full-row source/target reconciliation and deterministic run identity.
- SQL management and control queries.
- Excel and HTML management artefacts.
- Operational manifest with artefact SHA-256 fingerprints.
- GitHub Actions CI and a recurring scheduled workflow.
- Container build and execution in CI.

## Not demonstrated

- Microsoft Excel / Power Query Desktop runtime execution.
- Live HTTP authentication, pagination or rate-limit handling.
- A production cloud warehouse or high-concurrency database.
- Enterprise secret rotation, SSO/RBAC or production credential management.
- External email delivery or publication to a live BI service.
- Retry queues, dead-letter handling, pager/on-call integration or SLA monitoring.
- Production throughput, latency, availability or disaster-recovery evidence.
- A live client integration or measured client ROI.

SQLite and synthetic sources are used to make the control logic executable and reviewable
without external infrastructure. The scheduled GitHub workflow proves recurring automation,
not production-grade orchestration.
