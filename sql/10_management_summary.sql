SELECT
    period,
    entity,
    COUNT(*) AS record_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS average_amount
FROM raw_reporting
GROUP BY period, entity
ORDER BY period, total_amount DESC, entity;
