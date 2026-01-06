INSERT INTO tutor_testprep_silver.dim_tutors
WITH params AS (
	SELECT TIMESTAMP '2026-01-01 00:00:00' AS slv_ingest_ts
)
SELECT
    ROW_NUMBER() OVER (ORDER BY tutor_id, ingest_ts)
      + COALESCE((SELECT MAX(tutor_sk) FROM tutor_testprep_silver.dim_tutors), 0) AS tutor_sk,
    CAST(tutor_id AS INT)                AS tutor_id,
    first_name,
    last_name,
    sex,
    CAST(date_of_birth AS DATE)           AS date_of_birth,
    CAST(contract_rate AS DECIMAL(10,2))  AS contract_rate,
    CAST(active_students AS INT)          AS active_students,
    CAST(created AS TIMESTAMP)            AS created_ts,
    CAST(updated AS TIMESTAMP)            AS updated_ts,
    CAST(
      CASE
        WHEN change_type = 'UPDATE' THEN updated
        ELSE created
      END AS TIMESTAMP
    )                                     AS effective_start_ts,

    TIMESTAMP '9999-12-31 23:59:59'       AS effective_end_ts,
    true                                  AS is_current,
    source_batch_id,
    p.slv_ingest_ts
FROM tutor_testprep_raw.tutors
CROSS JOIN params p
WHERE 1=1
AND change_type IN ('INSERT', 'UPDATE')
