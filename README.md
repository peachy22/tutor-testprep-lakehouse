# tutor-testprep-lakehouse
A complete OLTP->OLAP data pipeline for a tutoring company, featuring operational simulation in python, ELT workflows, dimensional modeling (star schema), SCD2 tracking, orchestration, and dashboard-ready analytics.

├───data
│   └───raw
│       ├───sessions
│       │   └───ingest_date=2025-12-19
│       │           sessions.csv
│       │
│       ├───students
│       │   └───ingest_date=2025-12-19
│       │           students.csv
│       │
│       └───tutors
│           └───ingest_date=2025-12-19
│                   tutors.csv
│
└───src
    ├───simulation
    │
    └───utils
        │   business_sim_analytics.pbix
        │   business_sim_historical.py
        │   business_sim_incremental.py
        │   lists.py
