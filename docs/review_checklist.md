# Technical review checklist

Use this checklist when reviewing a change to the reporting control chain.

- Source contracts fail closed on unexpected structure.
- Cross-source business keys remain unique.
- Invalid inputs cannot overwrite the last valid published snapshot.
- A smaller current source removes stale target records.
- Source, staging and published target reconcile on material fields.
- SQL controls reference the latest published snapshot.
- Excel rejects are visible in the data-quality log.
- Power Query source-code claims remain separate from Desktop runtime claims.
- Operational artefacts are fingerprinted in the run manifest.
- Repeated source state remains idempotent and auditable.
- CI executes tests, reverse tests, Excel generation and the container runtime.
- Scheduled execution publishes an inspectable evidence bundle.
- Limitations remain explicit when production evidence is absent.
