
CREATE EXTERNAL TABLE raw_sessions (
  session_id        STRING,
  student_id        STRING,
  tutor_id          STRING,
  subject_id        STRING,
  stamp             TIMESTAMP,
  duration          DOUBLE,
  status            STRING,
  source_batch_id   STRING,
  ingest_ts         TIMESTAMP
)
PARTITIONED BY (
  ingest_date       DATE
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = ',',
  'field.delim' = ',',
  'escape.delim' = '\\',
  'timestamp.formats' = 'yyyy-MM-dd HH:mm:ss,yyyy-MM-dd HH:mm:ss.SSS'
)
STORED AS TEXTFILE
LOCATION 's3://tutor-testprep-lakehouse/raw/sessions/'
TBLPROPERTIES (
    'skip.header.line.count' = '1'
);


