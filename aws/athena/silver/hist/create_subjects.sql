INSERT INTO dim_subjects
WITH params AS (
	SELECT TIMESTAMP '2026-12-31 01:00:00' AS slv_ingest_ts
)
SELECT x.*, p.slv_ingest_ts FROM (
SELECT 1, 'SAT/ACT/PSAT+'
UNION ALL
SELECT 2, 'Math'
UNION ALL
SELECT 3, 'Science'
UNION ALL
SELECT 4, 'Foreign Language'
UNION ALL
SELECT 5, 'Language Arts'
UNION ALL
SELECT 6, 'Social Studies'
UNION ALL
SELECT 0, 'Other'
) x CROSS JOIN params p
