# Excel / Power Query validation

## Evidence boundary

The repository contains two complementary implementations:

- **Python + openpyxl** — executable reference implementation used in CI to generate and validate the Excel workbooks.
- **Power Query M** — analyst-facing transformation asset intended to be loaded in Microsoft Excel or Power BI.

The M script is versioned source code. It is not described as runtime-validated by Microsoft Excel until a Desktop execution artefact is captured.

## Source workbook

`python -m reporting_pipeline.cli excel-demo` creates `output/source_messy_reporting.xlsx` with:

- `Raw_Transactions` — mixed casing, locale-formatted currency, a duplicate key, invalid amount, negative amount, missing period, unmapped entity and non-reportable status;
- `Entity_Map` — canonical entity mapping;
- `Parameters` — reporting period, required status, currency and control mode.

The defects are deterministic and intentional. They are test fixtures, not accidental bad data.

## Management workbook

The same command creates `output/clean_management_report.xlsx` with:

- `Executive_Summary`;
- `Clean_Data`;
- `Data_Quality_Log`;
- `Reconciliation`;
- `Parameters`.

The output preserves accepted source-row lineage, logs rejected/flagged rows and exposes reconciliation controls instead of silently deleting bad records.

## Power Query setup

Create a text parameter named `pSourcePath` in Power Query and point it to the generated source workbook. Paste `powerquery/clean_reporting_source.m` into a blank query.

The query enforces the expected columns with `MissingField.Error`, normalises text and European decimal strings, applies types, filters reportable rows and deduplicates the business key.

## Reverse tests

CI verifies:

1. workbook schema drift fails closed;
2. duplicate and invalid source rows are surfaced in the DQ log;
3. accepted rows reconcile;
4. the generated management workbook can be reopened;
5. the Power Query asset contains the explicit source-path parameter and schema contract.

The remaining gap is Microsoft Excel / Power Query Desktop runtime evidence.
