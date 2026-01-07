MERGE INTO tutor_testprep_silver.dim_tutors t
USING (
    SELECT DISTINCT
        CAST(tutor_id AS INT) AS tutor_id,
        MIN(updated) AS effective_end_ts
    FROM tutor_testprep_raw.tutors
    WHERE change_type = 'UPDATE'
    GROUP BY CAST(tutor_id AS INT)
) s
ON t.tutor_id = s.tutor_id
AND t.is_current = true
WHEN MATCHED THEN
  UPDATE SET
    effective_end_ts = s.effective_end_ts,
    is_current = false
