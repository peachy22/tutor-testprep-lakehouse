CREATE TABLE tutor_testprep.students_stats
WITH (    table_type = 'ICEBERG',
    format = 'PARQUET',
    location = 's3://tutor-testprep-lakehouse/gold/students_stats/',
    is_external = false
) AS

WITH billable_session_stats AS (
    SELECT
        s.student_id,
        MIN(s.session_ts) AS first_session_ts,
        MAX(s.session_ts) AS last_session_ts,
        COUNT(*)              AS lifetime_billable_sessions
    FROM tutor_testprep_silver.fct_sessions s
    WHERE s.session_ts IS NOT NULL
    AND s.status <> 2
    GROUP BY s.student_id
),

   nonbillable_session_stats AS (
    SELECT
        student_id,
        COUNT(*)              AS lifetime_cancelled_sessions
    FROM tutor_testprep_silver.fct_sessions
    WHERE session_ts IS NOT NULL
    AND status = 2
    GROUP BY student_id
)

SELECT
    s.student_id,

    s.first_name,
    s.last_name,
    s.sex,
    s.date_of_birth,
    s.grade,
    s.status,
    s.contract_rate,
    (SELECT b.subject_name 
    FROM tutor_testprep_silver.fct_sessions x 
    INNER JOIN tutor_testprep_silver.dim_subjects b ON x.subject_id = b.subject_id
    WHERE x.student_id = s.student_id
    ORDER BY x.session_ts DESC LIMIT 1) AS current_subject,
    (SELECT b.last_name || ', ' || b.first_name 
    FROM tutor_testprep_silver.fct_sessions x 
    INNER JOIN tutor_testprep_silver.dim_tutors b ON x.tutor_id = b.tutor_id
    WHERE x.student_id = s.student_id
    ORDER BY x.session_ts DESC LIMIT 1) AS current_tutor,
    bss.first_session_ts,
    bss.last_session_ts,
    bss.lifetime_billable_sessions,
    COALESCE(nss.lifetime_cancelled_sessions,0) AS lifetime_cancelled_sessions,

    (SELECT MAX(slv_ingest_ts) FROM tutor_testprep_silver.fct_sessions) AS as_of_ts

FROM tutor_testprep_silver.dim_students s
LEFT JOIN billable_session_stats bss ON s.student_id = bss.student_id
LEFT JOIN nonbillable_session_stats nss ON s.student_id = nss.student_id
WHERE s.is_current = true
AND s.status = 'Active'