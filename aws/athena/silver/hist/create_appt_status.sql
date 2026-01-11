INSERT INTO dim_appt_status
WITH params AS (
	SELECT TIMESTAMP '2026-12-31 01:00:00' AS slv_ingest_ts
)
SELECT x.*, p.slv_ingest_ts FROM (
SELECT 0, 'Completed'
UNION ALL
SELECT 1, 'No-Show'
UNION ALL
SELECT 2, 'Cancelled'
) x CROSS JOIN params p