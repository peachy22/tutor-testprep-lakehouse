
CREATE EXTERNAL TABLE raw_tutors (
tutor_id string,
first_name string,
last_name string,
sex string,
date_of_birth string,
contract_rate string,
active_students string,
created timestamp,
updated timestamp,
change_type string,
source_batch_id string,
ingest_ts timestamp
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
LOCATION 's3://tutor-testprep-lakehouse/raw/tutors/'
TBLPROPERTIES (
    'skip.header.line.count' = '1'
);

