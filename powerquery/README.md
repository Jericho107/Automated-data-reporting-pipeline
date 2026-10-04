# Power Query evidence

`clean_reporting_source.m` is a version-controlled Power Query M transformation asset for the Excel case study.

It implements the analyst-facing transformation path:

- enforce the expected transaction and mapping columns;
- trim business keys and normalise entity/status text;
- parse European-formatted amount strings with a fail-safe `try ... otherwise null`;
- join `Entity_Map` and retain only mapped entities;
- reject missing periods, invalid/negative amounts and non-approved records;
- deduplicate the reporting business key;
- preserve the original Excel source-row number for lineage.

The Python implementation in `reporting_pipeline.excel` remains the executable reference used by CI because GitHub-hosted Linux runners do not execute the Microsoft Excel Power Query engine.

The repository therefore does **not** claim Power Query Desktop runtime validation or exact engine parity until the M query is executed in Microsoft Excel/Power BI Desktop and a runtime artefact is captured.

This separation is deliberate: reviewable source-code evidence is not presented as Desktop runtime evidence.
