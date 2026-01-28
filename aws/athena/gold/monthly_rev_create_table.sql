CREATE TABLE tutor_testprep.monthly_rev
WITH (    table_type = 'ICEBERG',
    format = 'PARQUET',
    location = 's3://tutor-testprep-lakehouse/gold/monthly_rev/',
    is_external = false
) AS

SELECT DATE_FORMAT(ses.session_date,'%M %Y') AS Month,
       SUM(stu.contract_rate*ses.duration) AS Revenue,
       CONCAT(tut.last_name,', ',tut.first_name) AS Contractor,
       SUM(ses.duration) AS Hours,
       SUM(tut.contract_rate*ses.duration) AS Expense,
       sub.subject_name AS Subject
FROM tutor_testprep_silver.fct_sessions ses 
INNER JOIN tutor_testprep_silver.dim_students stu on stu.student_id = ses.student_id AND stu.is_current = true
INNER JOIN tutor_testprep_silver.dim_tutors tut on tut.tutor_id = ses.tutor_id and tut.is_current = true
INNER JOIN tutor_testprep_silver.dim_appt_status apt on apt.status_id = ses.status
INNER JOIN tutor_testprep_silver.dim_subjects sub on sub.subject_id = ses.subject_id
GROUP BY DATE_FORMAT(ses.session_date,'%M %Y'), sub.subject_name, CONCAT(tut.last_name,', ',tut.first_name)