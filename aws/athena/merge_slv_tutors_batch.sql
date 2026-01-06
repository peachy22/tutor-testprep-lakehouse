MERGE INTO tutor_testprep_silver.dim_tutors t
USING (
    SELECT
        CAST(tutor_id AS INT) AS tutor_id,
        updated AS effective_end_ts
    FROM tutor_testprep_raw.tutors
    WHERE change_type = 'UPDATE'
) s
ON t.tutor_id = s.tutor_id
AND t.is_current = true
WHEN MATCHED THEN
  UPDATE SET
    effective_end_ts = s.effective_end_ts,
    is_current = false,
    updated_ts = s.effective_end_ts;
