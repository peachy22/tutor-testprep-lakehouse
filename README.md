# OLTP → OLAP Data Engineering Project

## Overview

This repository demonstrates an end-to-end OLTP-to-OLAP data engineering pipeline designed to simulate a production-grade analytics platform for an education and tutoring company. The project emphasizes event-driven ingestion, lakehouse architecture, dimensional modeling, and BI-facing gold artifacts.

The primary objective is to simulate raw transactional data, then translate that output into analytically useful, well-modeled datasets that support reporting, dashboards, and downstream decision-making.

## ETL Architecture Summary

The pipeline follows a layered lakehouse architecture deployed on AWS-managed services:

• **Raw (Bronze)** – Synthetic OLTP-style CSV data landed in S3c  
• **Silver** – Cleaned, conformed, and relationally consistent tables in Athena  
• **Gold** – Analytics-ready fact and dimension tables, plus business-facing aggregates

Processing is orchestrated via AWS Lambda and EventBridge, with Athena serving as the SQL execution engine. While the core pipeline is AWS-native, curated gold-layer artifacts are exported to Google Cloud via the Drive API, decoupling analytical compute from downstream consumption. For higher-concurrency or latency-sensitive workloads, this architecture would naturally evolve toward a dedicated warehouse such as Redshift paired with an AWS-native enterprise BI tool like Quicksight; Athena + Looker is used here deliberately to emphasize cost efficiency, elasticity, and operational simplicity under moderate analytical load.

## Data Model

### Source (OLTP-style) Concepts

The synthetic source data simulates a tutoring platform with:

• Students (SCD2)\\
• Tutors (SCD2)\\
• Tutoring Sessions (Fact)

Specific simulation behaviors and probabilities are documented in the .py files at src/utils. The key behaviors are as follows, based upon my real-world experience in the test prep domain:

• The business primarily serves year-round standardized test preparation clients (e.g., SAT, PSAT)\\
• Students schedule one session per week, with a certain probability to cancel each, either with sufficient notice (not billable) or not (billable)\\
• Student churn is modeled by checking against a quit probability for each session that is scheduled to occur\\
• Students will always churn at the beginning of summer (school work support) or after 120 days of test prep (standardized testing)\\
• During the fall, students exhibit probability of returning for sessions provided they have not graduated yet\\
• Tutors are contracted with flexible subject coverage, but are capped at a maximum active student load\\
• Client and tutor onboarding rates are seasonal, peaking in the fall, in addition to increasing gradually overall as the business matures

Prior to 2026-01-01, the data is modeled in a historical batch that represents the state of the business pre-migration to AWS. After that, data is batch simulated each day and SCD2-type tracking begins. This repo contains that initial simulated history in csv format.

The datasets which land in the raw zone are intentionally denormalized and imperfect to reflect real-world ingestion challenges. Simulated session facts get corrupted at a rate of 7%, with specific modes documented in src/utils/business_sim_incremental.py. Each batch simulation also appends non-corrupted rows to a simulation zone so that the history can reliably inform the realistic behavior of the next day. Note that at present, the dimension tables do not have simulated corruption. 

### Silver Layer (Conformed Tables)

The silver layer enforces data quality, typing, and relational integrity. Key tables include:

• `dim_students` (SCD2)\\
• `dim_tutors` (SCD2)\\
• `dim_subjects`\\
• `dim_appt_status`\\
• `fct_sessions`

All identifiers are stable and suitable for dimensional joins. 

Athena SQL ingests rows from raw staging in S3. New facts and dimensions are appended after normalization; dimension updates are merged. The normalization assumptions for session facts include:

• Fill null rows with assumed default values\\
    • The duration is 1 hour\\
    • The subject is Standardized Test Prep\\
• Double-digit durations are in minutes; convert to hours\\
• Duplicate entries should take the most recent stamped row\\
• Set future session dates to the current sim date

### Gold Layer (Analytics Artifacts)

The gold layer contains business-facing datasets optimized for BI tools and ad hoc analysis. Examples include:

• Active students profiles\\
• Contractor utilization\\
• Subject demand trends\\
• Revenue cycle

Gold artifacts are materialized as Athena tables for maximum AWS compute cost optimization. These tables are queried by Looker at its maximum refresh cycle of 12 hours. 

## Orchestration and Automation

### Event-Driven Ingestion

• Lambda for raw session generation for the previous date occurs via Eventbridge scheduler at 1am each morning\\ 
• Eventbridge custom event handler for Silver ingestion Lambda listents for successful raw loads\\
• Eventbridge custom event handler for Gold materialization Lambda listents for successful silver ingests\\
• Eventbridge custom event handler for Drive API Lambda listens for successful gold materializations

## Technologies Used

• **AWS S3** – Data lake storage\\
• **AWS Athena** – SQL query engine\\
• **AWS Lambda** – Serverless transformations\\
• **Amazon EventBridge** – Pipeline orchestration\\
• **Python** – Data generation and transformation logic\\
• **SQL** – Modeling and analytics\\
• **Looker Studio** – BI visualization (downstream consumer)\\
• **IAM** – Role-based permissions

## Project Structure

```
├───aws
│   ├───athena
│   │   ├───bronze
│   │   │   └───ddl                         -- athena table creation
│   │   ├───gold
│   │   └───silver
│   │       ├───batch                       -- daily batch merge (SCD2 tables) and insert scripts
│   │       ├───ddl                         -- athena table creation
│   │       └───hist                        -- initial historical (pre-migration) data load
│   ├───cmd                                 -- shell commands for syncing initial simulation results to s3
│   └───lambda                              -- custom package layers and code ready to run on lambda
├───data                                    -- pre-migration raw history
│   └───raw
│       ├───sessions
│       │   └───ingest_date=2025-12-31
│       ├───students
│       │   └───ingest_date=2025-12-31
│       └───tutors
│           └───ingest_date=2025-12-31
└───src
    ├───images                             -- architecture diagram
    ├───simulation                         -- pristine simulation data for informing subsequent batch runs
    └───utils                              -- simulator python files
```

## Intended Use

This project is designed as a portfolio artifact demonstrating:

• Practical data modeling\\
• Cloud-native orchestration\\
• Operations-oriented thinking\\
• Production-aligned engineering tradeoffs

## Future Enhancements

• Corruption modes for simulated dimension tables\\
• Data quality checks and expectations\\
• CI validation of SQL artifacts\\
• Migration to AWS Step Functions\\
    • Robust AWS-native error handling and retry rules\\
• Enhancements to simulation realism:\\
    • Contractor churn\\
    • College-level clients\\
    • Client feedback / test score analytics\\
    • Multiple sessions per week during finals / burst periods

## Disclaimer

All data in this repository is synthetic. No real student or contractor information is used.

