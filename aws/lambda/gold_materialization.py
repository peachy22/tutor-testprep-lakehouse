import boto3
import time
import logging
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
import json
import logging

events_client = boto3.client("events")
s3 = boto3.client("s3") 

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

ATHENA_DATABASE = "tutor_testprep"
ATHENA_OUTPUT = "s3://tutor-testprep-lakehouse/athena/lambda/" 
ATHENA_WORKGROUP = "primary"

athena = boto3.client("athena")

SQL_BUCKET = "tutor-testprep-lakehouse"
SQL_PREFIX = "gold/sql/gold_materialization/"

sql_files = [
           "active_students_drop_table.sql",
            "active_students_create_table.sql",
            "monthly_rev_drop_table.sql",
            "monthly_rev_create_table.sql"
        ]

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

def build_materialization_completed_event():
    return {
        "status": "SUCCESS",
        "emitted_at": datetime.now(timezone.utc).isoformat(),
        "executed_queries": sql_files
    }

def emit_materialization_completed_event(detail: dict) -> None:
    response = events_client.put_events(
        Entries=[
            {
                "Source": "tutor.gold.materialization",
                "DetailType": "MaterializationCompleted",
                "Detail": json.dumps(detail),
                "EventBusName": "default" 
            }
        ]
    )
    entry = response["Entries"][0]
    if "ErrorCode" in entry:
        raise RuntimeError(
            f"Failed to emit MaterializationCompleted event: "
            f"{entry['ErrorCode']} - {entry.get('ErrorMessage')}"
        )

def lambda_handler(event, context):
    LOGGER.info("Starting Athena gold materialization")
    try:    

        for sql_file in sql_files:
            LOGGER.info(f"Executing {sql_file}")
            sql = load_sql(sql_file)
            query_id = run_athena_query(sql)
            wait_for_query(query_id)

        event_detail = build_materialization_completed_event()
        emit_materialization_completed_event(event_detail)

        LOGGER.info("Gold layer materialization completed successfully")

        return event_detail

    except Exception:
        LOGGER.exception("Gold layer materialization failed")
        raise
