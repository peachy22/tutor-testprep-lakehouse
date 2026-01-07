INSERT INTO tutor_testprep_silver.dim_students
WITH params AS (
	SELECT TIMESTAMP '2026-12-31 01:00:00' AS slv_ingest_ts
)
SELECT
    CAST(student_id AS INT) AS student_sk,
    CAST(student_id AS INT)               AS student_id,
    first_name,
    last_name,
    sex,
    CAST(date_of_birth AS DATE)           AS date_of_birth,
    CAST(grade AS INT)                    AS grade,
    status                                AS status,
    CAST(contract_rate AS DECIMAL(10,2))  AS contract_rate,
    CAST(created AS TIMESTAMP)            AS created_ts,
    CAST(updated AS TIMESTAMP)            AS effective_start_ts,
    TIMESTAMP '9999-12-31 23:59:59'       AS effective_end_ts,
    true                                  AS is_current,
    CASE WHEN source_batch_id IS NULL THEN 'migration' ELSE source_batch_id END AS source_batch_id,
    CASE WHEN source_batch_id IS NULL THEN p.slv_ingest_ts ELSE ingest_ts END AS raw_ingest_ts,
    p.slv_ingest_ts
FROM tutor_testprep_raw.students
CROSS JOIN params p
WHERE 1=1
AND change_type IS NULL
 
