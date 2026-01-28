import json
import boto3
import pandas as pd
from pyathena import connect
import gspread
from google.oauth2.service_account import Credentials

S3_BUCKET = "tutor-testprep-lakehouse"
SERVICE_ACCOUNT_KEY = "google/service_account.json"

def load_service_account_credentials():
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=S3_BUCKET, Key=SERVICE_ACCOUNT_KEY)
    key_dict = json.loads(obj["Body"].read().decode("utf-8"))

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    return Credentials.from_service_account_info(key_dict, scopes=scopes)

def lambda_handler(event, context):
    creds = load_service_account_credentials()
    gc = gspread.authorize(creds)

    sheet = gc.open("tutor_testprep_gold_rev")
    worksheet = sheet.worksheet("monthly")

    conn = connect(
        s3_staging_dir="s3://tutor-testprep-lakehouse/athena/query-results/", 
        region_name="us-east-1",
        schema_name="tutor_testprep"
    )

    sql = """
        select * from monthly_rev
    """

    df = pd.read_sql(sql, conn)
    df = df.fillna("").astype(str)

    worksheet.clear()
    worksheet.update(
        [df.columns.tolist()] + df.values.tolist(),
        value_input_option="RAW"
    )

    return {"status": "SUCCESS"}
