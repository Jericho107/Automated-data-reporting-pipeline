WITH target AS (
    SELECT
        COUNT(*) AS target_rows,
        ROUND(SUM(amount), 2) AS target_total
    FROM raw_reporting
)
SELECT
    r.run_id,
    r.source_rows,
    t.target_rows,
    r.source_rows - t.target_rows AS row_delta,
    r.source_total,
    t.target_total,
    ROUND(r.source_total - t.target_total, 2) AS amount_delta,
    CASE
        WHEN r.source_rows = t.target_rows
         AND ROUND(r.source_total - t.target_total, 2) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS reconciliation_status
FROM pipeline_runs r
CROSS JOIN target t
ORDER BY r.run_id;
