SELECT
    run_id,
    source_rows,
    source_total,
    source_checksum,
    status,
    execution_count,
    last_executed_at
FROM pipeline_runs
ORDER BY last_executed_at DESC, run_id;
