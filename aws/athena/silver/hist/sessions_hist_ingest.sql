 INSERT INTO tutor_testprep_silver.fct_sessions (
     session_id,
     student_id,
     tutor_id,
     subject_id,
     session_ts,
     session_date,
     duration,
     status,
     source_batch_id,
	 raw_ingest_ts,
     slv_ingest_ts
 )
WITH params AS (
	SELECT TIMESTAMP '2025-12-31 01:00:00' AS slv_ingest_ts
),
latest_tutor AS (
	SELECT student_id,
		MAX(tutor_id) AS last_tutor_id
	FROM tutor_testprep_raw.sessions
	WHERE tutor_id IS NOT NULL
	GROUP BY student_id
),
ranked AS (
	SELECT s.session_id AS raw_session_id,
	    CAST(s.session_id AS INT) AS session_id,
	    s.student_id AS raw_student_id,
		CAST(s.student_id AS INT) AS student_id,
		s.tutor_id AS raw_tutor_id,
		COALESCE(
			CAST(CAST(NULLIF(s.tutor_id,'') AS DOUBLE) AS INT),
			CAST(CAST(NULLIF(s.tutor_id,'') AS DOUBLE) AS INT),
			0
		) AS tutor_id,
		s.subject_id AS raw_subject_id,
		CAST(NULLIF(s.subject_id,'') AS INT) AS subject_id,
		s.stamp AS raw_stamp,
		CAST(
			CASE
				WHEN s.stamp IS NULL THEN p.slv_ingest_ts
				WHEN s.stamp > p.slv_ingest_ts THEN p.slv_ingest_ts 
				ELSE s.stamp
			END AS TIMESTAMP
		) AS session_ts,
		s.duration AS raw_duration,
			CASE
				WHEN NULLIF(s.duration,'') IS NULL THEN 1.0
				WHEN CAST(NULLIF(s.duration,'') AS DOUBLE) >= 60.0 THEN CAST(NULLIF(s.duration,'') AS DOUBLE) / 60.0 
				ELSE CAST(NULLIF(s.duration,'') AS DOUBLE)
			END AS duration,
		s.status AS raw_status,
		COALESCE(CAST(CAST(NULLIF(s.status,'') AS DOUBLE) AS INT),0) AS status,
		CASE WHEN s.source_batch_id IS NULL THEN 'migration' ELSE s.source_batch_id END AS source_batch_id,
        CASE WHEN source_batch_id IS NULL THEN p.slv_ingest_ts ELSE ingest_ts END AS raw_ingest_ts,
		s.ingest_ts AS source_ingest_ts,
		p.slv_ingest_ts,
		CAST(
			CASE
				WHEN s.stamp IS NULL THEN p.slv_ingest_ts
				WHEN s.stamp > p.slv_ingest_ts THEN p.slv_ingest_ts ELSE s.stamp
			END AS DATE
		) AS session_date,
		CASE WHEN s.tutor_id = '' OR
		          s.subject_id = '' OR
		          s.duration = '' OR
		          s.status = '' THEN 'ERR_INVALID_DESCRIPTOR'
			 WHEN CAST(s.duration AS DOUBLE) > 60 THEN 'ERR_UNITS_RANGE'
		     WHEN s.stamp > p.slv_ingest_ts THEN 'ERR_INVALID_STAMP' END AS err_desc,
		ROW_NUMBER() OVER (
			PARTITION BY s.session_id
			ORDER BY CAST(s.stamp AS TIMESTAMP) DESC NULLS LAST,
				p.slv_ingest_ts DESC
		) AS rn
	FROM tutor_testprep_raw.sessions s
		CROSS JOIN params p
		LEFT JOIN latest_tutor lt ON s.student_id = lt.student_id
	WHERE s.session_id IS NOT NULL
	AND s.source_batch_id IS NULL
)
SELECT 
    session_id,
	student_id,
	tutor_id,
	subject_id,
	session_ts,
	session_date,
	duration,
	status,
	source_batch_id,
    raw_ingest_ts,
	slv_ingest_ts
FROM ranked
WHERE 1=1
AND rn = 1
