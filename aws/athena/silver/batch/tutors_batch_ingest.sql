INSERT INTO tutor_testprep_silver.dim_tutors
WITH params AS (
	SELECT DATE_ADD('day', 1, MAX(slv_ingest_ts)) AS slv_ingest_ts FROM tutor_testprep_silver.fct_sessions 
),
    max_update_ts AS (
    SELECT CAST(tutor_id AS INT) AS tutor_id,
    MAX(updated) AS updated_ts
    FROM tutor_testprep_raw.tutors
    WHERE ingest_date = (SELECT CAST(slv_ingest_ts AS DATE) FROM params)
    GROUP BY CAST(tutor_id AS INT)
)
SELECT
    ROW_NUMBER() OVER (ORDER BY t.tutor_id, t.ingest_ts, t.updated)
      + COALESCE((SELECT MAX(tutor_sk) FROM tutor_testprep_silver.dim_tutors), 0) AS tutor_sk,
    CAST(t.tutor_id AS INT)                AS tutor_id,
    t.first_name,
    t.last_name,
    t.sex,
    CAST(t.date_of_birth AS DATE)           AS date_of_birth,
    CAST(t.contract_rate AS DECIMAL(10,2))  AS contract_rate,
    CAST(t.active_students AS INT)          AS active_students,
    CAST(t.created AS TIMESTAMP)            AS created_ts,
    p.slv_ingest_ts                         AS effective_start_ts,
    CAST('9999-12-31 23:59:59' AS TIMESTAMP)     AS effective_end_ts,
    CASE WHEN CAST(t.updated AS TIMESTAMP) = m.updated_ts THEN true ELSE false END AS is_current,
    CASE WHEN t.source_batch_id IS NULL THEN 'migration' ELSE source_batch_id END AS source_batch_id,
    ingest_ts AS raw_ingest_ts,
    p.slv_ingest_ts
FROM tutor_testprep_raw.tutors t
LEFT JOIN max_update_ts m ON CAST(m.tutor_id AS INT) = CAST(t.tutor_id AS INT)
CROSS JOIN params p
WHERE 1=1
AND change_type IN ('INSERT', 'UPDATE')
AND t.ingest_date = CAST((SELECT slv_ingest_ts FROM params) AS DATE)

