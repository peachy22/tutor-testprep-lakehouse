MERGE INTO tutor_testprep_silver.dim_students t
USING (
    SELECT
        CAST(student_id AS INT) AS student_id,
        updated AS effective_end_ts
    FROM tutor_testprep_raw.students
    WHERE change_type = 'UPDATE'
) s
ON t.student_id = s.student_id
AND t.is_current = true
WHEN MATCHED THEN
  UPDATE SET
    effective_end_ts = s.effective_end_ts,
    is_current = false,
    updated_ts = s.effective_end_ts;
