INSERT INTO tutor_testprep_silver.dim_students
WITH params AS (
	SELECT TIMESTAMP '2026-01-02 02:00:00' AS slv_ingest_ts
),
    max_update_ts AS (
    SELECT CAST(student_id AS INT) AS student_id,
    MAX(updated) AS updated_ts
    FROM tutor_testprep_raw.students
    GROUP BY CAST(student_id AS INT)
)
SELECT
    ROW_NUMBER() OVER (ORDER BY t.student_id, t.ingest_ts, t.updated)
      + COALESCE((SELECT MAX(student_sk) FROM tutor_testprep_silver.dim_students), 0) AS student_sk,
    CAST(t.student_id AS INT)               AS student_id,
    t.first_name,
    t.last_name,
    t.sex,
    CAST(t.date_of_birth AS DATE)           AS date_of_birth,
    CAST(t.grade AS INT)                    AS grade,
    t.status                                AS status,
    CAST(t.contract_rate AS DECIMAL(10,2))  AS contract_rate,
    CAST(t.created AS TIMESTAMP)            AS created_ts,
    p.slv_ingest_ts                         AS effective_start_ts,
    CAST('9999-12-31 23:59:59' AS TIMESTAMP)     AS effective_end_ts,
    CASE WHEN CAST(t.updated AS TIMESTAMP) = m.updated_ts THEN true ELSE false END AS is_current,
    CASE WHEN t.source_batch_id IS NULL THEN 'migration' ELSE source_batch_id END AS source_batch_id,
    t.ingest_ts AS raw_ingest_ts,
    p.slv_ingest_ts
FROM tutor_testprep_raw.students t
LEFT JOIN max_update_ts m ON CAST(m.student_id AS INT) = CAST(t.student_id AS INT)
CROSS JOIN params p
WHERE 1=1
AND change_type IN ('INSERT', 'UPDATE')
AND t.ingest_date = CAST((SELECT slv_ingest_ts FROM params) AS DATE)
