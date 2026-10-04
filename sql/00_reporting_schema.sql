CREATE TABLE IF NOT EXISTS raw_reporting (
    record_id TEXT PRIMARY KEY,
    period TEXT NOT NULL,
    entity TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount >= 0)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    source_rows INTEGER NOT NULL,
    source_total REAL NOT NULL,
    source_checksum TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PASS', 'FAIL')),
    execution_count INTEGER NOT NULL DEFAULT 1,
    last_executed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
