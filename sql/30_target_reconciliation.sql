WITH latest_run AS (
    SELECT
        run_id,
        source_rows,
        source_total,
        source_checksum,
        status,
        execution_count,
        last_executed_at
    FROM pipeline_runs
    ORDER BY last_executed_at DESC, rowid DESC
    LIMIT 1
),
target AS (
    SELECT
        COUNT(*) AS target_rows,
        ROUND(COALESCE(SUM(amount), 0), 2) AS target_total
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
         AND r.status = 'PASS'
        THEN 'PASS'
        ELSE 'FAIL'
    END AS reconciliation_status
FROM latest_run r
CROSS JOIN target t;
