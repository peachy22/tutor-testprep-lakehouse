CREATE TABLE dim_appt_status (
status_id INT,
status_name STRING,
updated TIMESTAMP
)
LOCATION 's3://tutor-testprep-lakehouse/silver/dim_appt_status/'
TBLPROPERTIES (
    'table_type' = 'ICEBERG'
);