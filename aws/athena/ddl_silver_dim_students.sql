CREATE TABLE dim_students (
    student_sk            BIGINT,
    student_id            INT,

    first_name            STRING,
    last_name             STRING,
    sex                   STRING,
    date_of_birth         DATE,
    grade                 INT,
    status                STRING,
    contract_rate         DECIMAL(10,2),

    created_ts            TIMESTAMP,
    updated_ts            TIMESTAMP,

    effective_start_ts    TIMESTAMP,
    effective_end_ts      TIMESTAMP,
    is_current             BOOLEAN,

    source_batch_id       STRING,
    ingest_ts             TIMESTAMP
)
LOCATION 's3://tutor-testprep-lakehouse/silver/dim_students/'
TBLPROPERTIES (
    'table_type' = 'ICEBERG'
);
