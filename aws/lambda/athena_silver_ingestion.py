import boto3
import time
import logging
from pathlib import Path

s3 = boto3.client("s3")

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

ATHENA_DATABASE = "tutor_testprep_silver"
ATHENA_OUTPUT = "s3://tutor-testprep-lakehouse/athena/lambda/"
ATHENA_WORKGROUP = "primary"

athena = boto3.client("athena")

SQL_BUCKET = "tutor-testprep-lakehouse"
SQL_PREFIX = "silver/sql/batch_process/"


def run_athena_query(sql: str) -> str:
    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": ATHENA_DATABASE},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
        WorkGroup=ATHENA_WORKGROUP,
    )

    query_execution_id = response["QueryExecutionId"]
    LOGGER.info(f"Started Athena query {query_execution_id}")
    return query_execution_id


def wait_for_query(query_execution_id: str, poll_seconds: int = 5) -> None:
    while True:
        response = athena.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        status = response["QueryExecution"]["Status"]["State"]

        if status == "SUCCEEDED":
            LOGGER.info(f"Query {query_execution_id} succeeded")
            return

        if status in ("FAILED", "CANCELLED"):
            reason = response["QueryExecution"]["Status"].get(
                "StateChangeReason", "Unknown"
            )
            raise RuntimeError(
                f"Athena query {query_execution_id} failed: {reason}"
            )

        time.sleep(poll_seconds)


def load_sql(filename: str) -> str:
    key = f"{SQL_PREFIX}{filename}"
    response = s3.get_object(
        Bucket=SQL_BUCKET,
        Key=key
    )
    return response["Body"].read().decode("utf-8")

def lambda_handler(event, context):
    LOGGER.info("Starting Silver layer Athena ingestion")

    sql_files = [
        "sessions_batch_ingest.sql",
        "students_batch_merge.sql",
        "students_batch_ingest.sql",
        "tutors_batch_merge.sql",
        "tutors_batch_ingest.sql"
    ]

    for sql_file in sql_files:
        LOGGER.info(f"Executing {sql_file}")
        sql = load_sql(sql_file)
        query_id = run_athena_query(sql)
        wait_for_query(query_id)

    LOGGER.info("Silver layer ingestion completed successfully")

    return {
        "status": "SUCCESS",
        "executed_queries": sql_files
    }
