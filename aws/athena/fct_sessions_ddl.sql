CREATE TABLE fct_sessions (
    session_id            INT,
    student_id            INT,
    tutor_id              INT,
    subject_id            INT,

    session_ts            TIMESTAMP,
    session_date          DATE,

    duration              DOUBLE,
    status                INT,

    source_batch_id       STRING,
    raw_ingest_ts         TIMESTAMP,
    slv_ingest_ts         TIMESTAMP
)
LOCATION 's3://tutor-testprep-lakehouse/silver/fct_sessions/'
TBLPROPERTIES (
    'table_type' = 'ICEBERG'
);
