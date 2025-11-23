# tutor-testprep-lakehouse
A complete OLTP->OLAP data pipeline for a tutoring company, featuring ELT workflows, dimensional modeling (star schema), SCD2 tracking, orchestration, and dashboard-ready analytics.

tutor-testprep-lakehouse/
│
├── data/
│   ├── raw/
│   ├── staged/
│   └── curated/
│
├── src/
│   ├── ingest/
│   │    └── ingest_raw_to_staged.py
│   ├── transform/
│   │    └── transform_staged_to_curated.py
│   ├── dq/
│   │    └── dq_checks.py
│   └── utils/
│        └── db_connection.py
│
├── sql/
│   ├── create_staging_tables.sql
│   ├── create_warehouse_tables.sql
│   ├── transformations/
│   │    └── staged_to_curated.sql
│   └── tests/
│        └── dq_queries.sql
│
├── orchestration/
│   └── prefect_flow.py
│
└── README.md
