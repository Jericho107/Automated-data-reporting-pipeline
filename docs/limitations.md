# Limitations

- Sources are synthetic CSV and JSON/API-style payloads.
- The JSON adapter demonstrates an API contract pattern but does not perform live HTTP authentication or pagination.
- SQLite is used to prove idempotency and reconciliation; production warehouses may require different transactional and concurrency controls.
- Scheduling, retry orchestration, secrets management and SLA monitoring are outside scope.
- The delivery artefact is static HTML and does not send email or publish to an external BI service.
- No production throughput, latency or client-impact claim is made.
