CREATE TABLE dim_tutors (
    tutor_sk              INT,
    tutor_id              INT,

    first_name            STRING,
    last_name             STRING,
    sex                   STRING,
    date_of_birth         DATE,
    contract_rate         DECIMAL(10,2),
    active_students       INT,

    created_ts            TIMESTAMP,
    updated_ts            TIMESTAMP,

    effective_start_ts    TIMESTAMP,
    effective_end_ts      TIMESTAMP,
    is_current            BOOLEAN,

    source_batch_id       STRING,
    slv_ingest_ts         TIMESTAMP
)
LOCATION 's3://tutor-testprep-lakehouse/silver/dim_tutors/'
TBLPROPERTIES (
    'table_type' = 'ICEBERG'
);
