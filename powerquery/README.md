# Power Query evidence

`clean_reporting_source.m` is a version-controlled Power Query M transformation asset for the Excel case study.

It demonstrates the analyst-facing transformation path: trim business keys, normalise entity/status text, convert locale-dependent amount strings, type columns, retain approved/non-negative rows and enforce business-key uniqueness.

The Python implementation in `reporting_pipeline.excel` is the executable reference used by CI because GitHub-hosted Linux runners do not execute the Excel Power Query engine. The repository therefore does **not** claim runtime parity with Microsoft Excel until the M query is executed in Excel/Power Query Desktop and evidence is captured.

This separation is deliberate: source code evidence is not presented as runtime evidence.
