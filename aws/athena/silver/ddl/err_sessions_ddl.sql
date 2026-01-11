CREATE TABLE err_sessions (

    raw_session_id          STRING,
    raw_student_id          STRING,
    raw_tutor_id            STRING,
    raw_subject_id          STRING,

    raw_stamp               TIMESTAMP,
    raw_duration            STRING,
    raw_status              STRING,

    source_batch_id         STRING,
    source_ingest_ts        TIMESTAMP,
    source_err_desc       STRING,
    slv_ingest_ts           TIMESTAMP
)
LOCATION 's3://tutor-testprep-lakehouse/silver/err_sessions/'
TBLPROPERTIES (
    'table_type' = 'ICEBERG'
);
