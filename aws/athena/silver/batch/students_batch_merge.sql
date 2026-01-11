
MERGE INTO tutor_testprep_silver.dim_students t
USING (
    SELECT DISTINCT
        CAST(student_id AS INT) AS student_id,
        (SELECT DATE_ADD('day', 1, MAX(slv_ingest_ts)) FROM tutor_testprep_silver.fct_sessions) AS effective_end_ts
    FROM tutor_testprep_raw.students
    WHERE change_type = 'UPDATE'
        AND ingest_date = CAST((SELECT DATE_ADD('day', 1, MAX(slv_ingest_ts)) FROM tutor_testprep_silver.fct_sessions) AS DATE)
) s
ON t.student_id = s.student_id
AND t.is_current = true
WHEN MATCHED THEN
  UPDATE SET
    effective_end_ts = s.effective_end_ts,
    is_current = false
