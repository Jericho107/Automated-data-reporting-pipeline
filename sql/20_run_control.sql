SELECT
    run_id,
    source_rows,
    source_total,
    source_checksum,
    status
FROM pipeline_runs
ORDER BY run_id;
