import pandas as pd
from pyathena import connect

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "google/service_account.json",
    scopes=SCOPES
)

gc = gspread.authorize(creds)

sheet = gc.open("tutor_testprep_gold_students")
worksheet = sheet.worksheet("students")

conn = connect(
    s3_staging_dir="s3://tutor-testprep-lakehouse/silver/",
    region_name="us-east-1"
)

sql = """
SELECT * FROM tutor_testprep.active_students order by last_session_ts desc
"""

df = pd.read_sql(sql, conn)
df = df.fillna("").astype(str)

worksheet.clear()
values = [df.columns.tolist()] + df.values.tolist()
worksheet.update(values, value_input_option="RAW")