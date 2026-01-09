CREATE TABLE dim_subjects (
subject_id INT,
subject_name STRING,
updated TIMESTAMP
)
LOCATION 's3://tutor-testprep-lakehouse/silver/dim_subjects/'
TBLPROPERTIES (
    'table_type' = 'ICEBERG'
);