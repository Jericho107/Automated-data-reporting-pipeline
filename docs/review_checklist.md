# Technical review checklist

- Source contracts fail closed on unexpected structure.
- Cross-source business keys remain unique.
- Invalid inputs cannot overwrite the last valid published snapshot.
- A smaller current source removes stale target records.
- Source, staging and published target reconcile on material fields.
- Cleaned Excel rows are the rows published by the operational SQL snapshot.
- SQL controls reference the latest published snapshot.
- Excel rejects remain visible in the data-quality log.
- Power Query source claims remain separate from Desktop runtime claims.
- Operational artefacts are fingerprinted in the run manifest.
- Repeated source state remains idempotent and auditable.
- CI executes tests, reverse tests, Excel generation and the container runtime.
- Scheduled execution publishes an inspectable evidence bundle.
- Limitations remain explicit where production evidence is absent.
