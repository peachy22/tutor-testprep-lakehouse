import pandas as pd
import numpy as np
import boto3
import io
from datetime import datetime, date, timedelta, timezone
import random
import json
import logging


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

events_client = boto3.client("events")  

GIRL_NAMES = [
    "Ava","Emma","Olivia","Sophia","Isabella","Mia","Amelia","Harper","Evelyn","Abigail",
    "Emily","Elizabeth","Sofia","Avery","Ella","Scarlett","Grace","Chloe","Victoria","Riley",
    "Aria","Lily","Aubrey","Zoey","Penelope","Hannah","Nora","Scarlet","Leah","Stella",
    "Hazel","Ellie","Violet","Aurora","Savannah","Brooklyn","Bella","Claire","Skylar","Lucy",
    "Paisley","Anna","Caroline","Nova","Genesis","Emilia","Kennedy","Samantha","Maya","Willow"
]
BOY_NAMES = [
    "Liam","Noah","Oliver","Elijah","James","William","Benjamin","Lucas","Henry","Theodore",
    "Jack","Levi","Alexander","Jackson","Mateo","Daniel","Michael","Mason","Sebastian","Ethan",
    "Logan","Owen","Samuel","Jacob","Asher","Aiden","John","Joseph","Wyatt","David",
    "Leo","Luke","Julian","Hudson","Grayson","Matthew","Ezra","Gabriel","Carter","Isaac",
    "Jayden","Luca","Anthony","Dylan","Lincoln","Thomas","Maverick","Elias","Josiah","Charles"
]
LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts"
]

sim_start = datetime(2021,8,24,12,0,)
sim_end = datetime(2027,12,31,0,0,0)

students = pd.read_csv('s3://tutor-testprep-lakehouse/simulation/students.csv')
students_helpers = pd.read_csv('s3://tutor-testprep-lakehouse/simulation/students_helpers.csv')
tutors = pd.read_csv('s3://tutor-testprep-lakehouse/simulation/tutors.csv')
sessions = pd.read_csv('s3://tutor-testprep-lakehouse/simulation/sessions.csv')
sessions_i = pd.read_csv('s3://tutor-testprep-lakehouse/simulation/sessions_i.csv')
sessions_f = pd.read_csv('s3://tutor-testprep-lakehouse/simulation/sessions_f.csv')

students['created'] = pd.to_datetime(students['created'])
students['updated'] = pd.to_datetime(students['updated'])
tutors['created'] = pd.to_datetime(tutors['created'])
tutors['updated'] = pd.to_datetime(tutors['updated'])
sessions['stamp'] = pd.to_datetime(sessions['stamp'])
sessions_i['stamp'] = pd.to_datetime(sessions_i['stamp'])
sessions_f['stamp'] = pd.to_datetime(sessions_f['stamp'])

tutor_count = tutors.shape[0]
student_count = students.shape[0]
active_student_count = students[students["status"] == 'Active'].shape[0]
session_count = sessions.shape[0]

def create_new_student(business_day,new_student_multiplier,student_count, active_student_count):
    i = 1
    while i <= new_student_multiplier:
        grade_level = random.choices([random.choice(range(6,8)),random.choice(range(9,12))],[.25,.75],k=1)[0]
        first_session_hour = random.choice(range(13,19))
        created = datetime(business_day.year, business_day.month, business_day.day, first_session_hour, 0, 0)
        age = grade_level + 6
        birth_year = business_day.year - age
        dob = datetime(birth_year,random.randint(1, 12),random.randint(1, 28))
        sex = random.choices(['M','F'],[.39,.61],k=1)[0]
        if business_day.year - sim_start.year < 2:
            contract = 80
        elif business_day.year - sim_start.year < 3:
            contract = 100
        else:
            contract = 120
        if sex == 'M':
            first_name = random.choice(BOY_NAMES)
        else:
            first_name = random.choice(GIRL_NAMES)
        last_name = random.choice(LAST_NAMES)
        students.loc[len(students)] = [student_count,first_name,last_name,sex,dob.date(),grade_level,"Active",contract,created,created]
        students_helpers.loc[len(students_helpers)] = [student_count,random.choice([5,6]),random.choice(range(1,30)),0,random.choice([9,10,11])]
        i = i + 1
        student_count += 1
        active_student_count += 1
    return student_count, active_student_count

def create_new_tutor(tutor_count):
    tutor_id = tutor_count
    age = random.choice(range(20,50))
    contract = random.choice([30,35,40,45,50])
    sex = random.choice(['M','F'])
    if sex == 'M':
        first_name = random.choice(BOY_NAMES)
    else:
        first_name = random.choice(GIRL_NAMES)
    last_name = random.choice(LAST_NAMES)
    dob = (datetime.today() + timedelta(days = random.randint(-600,0))) - timedelta(days=365*age)
    created = max(students["created"])
    tutors.loc[len(tutors)] = [tutor_id, first_name, last_name, sex, dob.date(), contract, 0, created, created]
    tutor_count += 1
    return tutor_id, tutor_count

def stochastic_churn(business_day, sim_start, sim_end, season):
    progress = (business_day - sim_start).days / (sim_end - sim_start).days
    progress = max(0, min(1, progress))  
    if season == 'fall':
        seasonal_factor = random.randint(1, 3)
    else:
        seasonal_factor = 1
    base_prob = (0.2 + 0.6 * progress) * seasonal_factor
    noise = random.gauss(0, 0.05)         
    new_student_prob = base_prob + noise
    new_student_prob = max(0, min(1, new_student_prob))
    base_mult = 1 + 2 * progress
    new_student_multiplier = int(base_mult)
    new_student_multiplier = random.choice([1, new_student_multiplier])
    base_churn = 0.0044
    churn_noise = random.uniform(0.8, 1.2)
    stochastic_churn_prob = base_churn * churn_noise
    student_tutor_ratio = 30
    return new_student_prob, new_student_multiplier, student_tutor_ratio, stochastic_churn_prob

# function for simulating new sessions each business day and triggering the creation of new students and tutors
def create_sessions(business_day, tutor_count, student_count, active_student_count, session_count, sim_start, sim_end):
    month = business_day.month
    if month in [9,10,11]:
        season = 'fall'
    elif month in [1,2,3,4,5,12]:
        season = 'spring'
    else:
        season = 'summer'
    # check if a new clien signs up today
    new_student_prob, new_student_multiplier, student_tutor_ratio, stochastic_churn_prob = stochastic_churn(business_day, sim_start, sim_end, season)
    if random.random() < new_student_prob:
        student_count, active_student_count = create_new_student(business_day,new_student_multiplier,student_count, active_student_count)
    for idx, row in students.iterrows():
        student_id = row["student_id"]
        student_helper = students_helpers[students_helpers["student_id"] == student_id]
        student_is_returnable = student_helper["returnable"].iloc[0]
        summer_cutoff_month = student_helper["summer_cutoff_month"].iloc[0]
        summer_cutoff_day = student_helper["summer_cutoff_day"].iloc[0]
        school_year_start_month = student_helper["school_year_start_month"].iloc[0]
        # students who will have their first session today:
        if student_id not in sessions_i["student_id"].values:
            # check for tutors who are available; if none are, hire a new one
            eligible = tutors.loc[tutors["active_students"] < student_tutor_ratio, "tutor_id"].tolist()
            if eligible:
                tutor_id = random.choice(eligible)
            else:
                tutor_id, tutor_count = create_new_tutor(tutor_count)
            subject_id = random.choices([1,2,random.choice([3,4]),random.choice([5,6])],[.3,.4,.2,.1],k=1)[0]
            # students may return the following year if they are not an SAT student
            if subject_id != 1:
                student_is_returnable = random.choices([1,0],[.4,.6],k=1)[0]
            else:
                student_is_returnable = 0
            stamp = row["created"]
            duration = random.choices([1,1.5,2],[.9,.05,.05],k=1)[0]
            sessions.loc[len(sessions)] = [session_count,student_id,tutor_id,subject_id,stamp,duration,0]
            sessions_i.loc[len(sessions_i)] = [session_count,student_id,tutor_id,subject_id,stamp,duration,0]
            sessions_f.loc[len(sessions_f)] = [session_count,student_id,tutor_id,subject_id,stamp,duration,0]
            students_helpers.loc[students_helpers["student_id"] == student_id, "returnable"] = student_is_returnable
            # increment the number of sessions for id and the client load for the selected tutor
            tutors.loc[tutors["tutor_id"] == tutor_id, "active_students"] += 1
            tutors.loc[tutors["tutor_id"] == tutor_id, "updated"] = stamp
            session_count += 1
            continue
        # students who are continuing their schedule today:
        elif row["status"] == "Active":
            first_session = sessions_i[sessions_i["student_id"] == student_id]
            first_session_date = first_session["stamp"].iloc[0].date()
            first_session_hour = first_session["stamp"].iloc[0].hour
            last_session = sessions_f[sessions_f["student_id"] == student_id]
            last_session_date = last_session["stamp"].iloc[0].date()
            curr_session_date = business_day.date()
            curr_session_year = business_day.year
            curr_session_hour = first_session_hour + random.choices([0,-1,1],[.8,.1,.1],k=1)[0]
            duration_delta = last_session_date-first_session_date
            duration_days = duration_delta.days
            subject_id = first_session["subject_id"].iloc[0]
            tutor_id = first_session["tutor_id"].iloc[0]
            stamp = datetime(curr_session_date.year, curr_session_date.month, curr_session_date.day, curr_session_hour, 0, 0)
            # students have a session once per week. If it has been a week since their last session:
            if (curr_session_date-last_session_date).days == 7:
                # the student will quit if they hit the random churn threshold, if they are an SAT student and they have prepped for enough time, or if their school year is over (they can return next year)
                if random.random() < stochastic_churn_prob or (duration_days > 120 and subject_id == 1) or (last_session_date > date(curr_session_year,summer_cutoff_month,summer_cutoff_day) and subject_id != 1):
                    students.loc[students["student_id"] == student_id, "status"] = 'Inactive'
                    students.loc[students["student_id"] == student_id, "updated"] = stamp
                    # the student is returnable if they were studying standard school work and quit at the end of their school year
                    if (last_session_date > date(curr_session_year,summer_cutoff_month,summer_cutoff_day) and subject_id != 1):
                        students_helpers.loc[students_helpers["student_id"] == student_id, "returnable"] = 1
                    else:
                        students_helpers.loc[students_helpers["student_id"] == student_id, "returnable"] = 0
                    # decrement the student load to free up the tutor
                    tutors.loc[tutors["tutor_id"] == tutor_id, "active_students"] -= 1
                    tutors.loc[tutors["tutor_id"] == tutor_id, "updated"] = stamp
                    active_student_count -= 1
                # the student will have a session, or a cancelled session, if they do not quit
                else:
                    last_session_hour = last_session["stamp"].iloc[0].hour
                    # the student's session time is roughly the same as their last one
                    duration = last_session["duration"].iloc[0]
                    # a student is 10% likely to cancel outright with notice - meaning no charge, 10% likely to cancel late or no-show- meaning we charge them. 
                    status = random.choices([0,1,2],[.8,.1,.1],k=1)[0]
                    sessions.loc[len(sessions)] = [session_count,student_id,tutor_id,subject_id,stamp,duration,status]
                    sessions_f.loc[sessions_f["student_id"] == student_id] = [session_count,student_id,tutor_id,subject_id,stamp,duration,status]
                    #increment the session ID
                    session_count += 1
            continue
        # if the student was not in grade 12 when they quit, left on good terms at the end of the school year, and today is around the start of the current school year, they will return for a session
        elif row["status"] == "Inactive" and row["grade"] < 12 and student_is_returnable == 1 and business_day.month == school_year_start_month and random.random() < .04:
            students.loc[students["student_id"] == student_id, "status"] = 'Active'
            # the student is now in the next grade level
            students.loc[students["student_id"] == student_id, "grade"] += 1
            students.loc[students["student_id"] == student_id, "updated"] = business_day
            last_session = sessions_f[sessions_f["student_id"] == student_id]
            last_tutor = last_session["tutor_id"].iloc[0]
            # the student prefers the tutor they were working with last
            preferred_tutor = tutors.loc[(tutors["active_students"] < student_tutor_ratio) & (tutors["tutor_id"] == last_tutor), "tutor_id"].tolist()
            eligible_tutors = tutors.loc[tutors["active_students"] < student_tutor_ratio, "tutor_id"].tolist()
            if preferred_tutor:
                tutor_id = preferred_tutor[0]
            elif eligible_tutors:
                tutor_id = random.choice(eligible_tutors)
            else:
                tutor_id, tutor_count = create_new_tutor(tutor_count)
            subject_id = random.choices([1,2,random.choice([3,4]),random.choice([5,6])],[.2,.5,.2,.1],k=1)[0]
            curr_session_date = business_day.date()
            duration = last_session["duration"].iloc[0]
            session_hour = random.choice(range(13,19))
            stamp = datetime(curr_session_date.year, curr_session_date.month, curr_session_date.day, session_hour, 0, 0)
            sessions.loc[len(sessions)] = [session_count,student_id,tutor_id,subject_id,stamp,duration,0]
            sessions_i.loc[sessions_f["student_id"] == student_id] = [session_count,student_id,tutor_id,subject_id,stamp,duration,0]
            sessions_f.loc[sessions_f["student_id"] == student_id] = [session_count,student_id,tutor_id,subject_id,stamp,duration,0]
            # active student counts and session ids increment
            tutors.loc[tutors["tutor_id"] == tutor_id, "active_students"] += 1
            tutors.loc[tutors["tutor_id"] == tutor_id, "updated"] = stamp
            session_count += 1
            active_student_count += 1
            continue
    return tutor_count, student_count, active_student_count, session_count

# the daily simulation begins after the last date in the history
inc_hist_start = max(sessions_f["stamp"]).date() + timedelta(days=1)

bd = pd.Timestamp(inc_hist_start).normalize()
ingest_stamp = bd + timedelta(days = 1)
ingest_date_folder = f"ingest_date={ingest_stamp.strftime('%Y-%m-%d')}"

# create today's data and append it to the history
tutor_count, student_count, active_student_count, session_count = create_sessions(bd, tutor_count, student_count, active_student_count, session_count, sim_start, sim_end)

# extract the sessions that were created today and prep for ingestion
new_sessions = sessions[sessions["stamp"].dt.date == bd.date()].copy()
new_sessions["source_batch_id"] = f"sim_{ingest_stamp.date()}"
new_sessions["ingest_ts"] = ingest_stamp + timedelta(milliseconds=random.randint(1,500))

# sessions ingested this way have certain chances to be corrupted or duplicated, necessitating cleansing in the silver layer
duplicate_rows = []
for idx, row in new_sessions.iterrows():
    base = row.copy()
    if random.random() < 0.07:  # 7% dirty rows total
        # mutually exclusive corruption modes
        corruption_roll = random.random()
        if corruption_roll < 0.25:
            # mnit error: hours emitted as minutes
            base["duration"] = base["duration"] * 60
        elif corruption_roll < 0.45:
            # missing duration
            base["duration"] = None
        elif corruption_roll < 0.60:
            # missing tutor assignment
            base["tutor_id"] = None
        elif corruption_roll < 0.75:
            # missing status
            base["status"] = None
        elif corruption_roll < 0.90:
            # backdated session (late-arriving event)
            base["stamp"] = base["stamp"] - timedelta(days=random.randint(1, 30))
        else:
            # future-dated session (clock skew / bad source)
            base["stamp"] = base["stamp"] + timedelta(days=random.randint(1, 30))
    new_sessions.loc[idx] = base
    dup_roll = random.random()
    # 2% total duplication rate
    if dup_roll < 0.02:
        dup = base.copy()
        dup["ingest_ts"] = ingest_stamp + timedelta(
            milliseconds=random.randint(1, 500)
        )
        # decide duplicate type (mutually exclusive)
        dup_type = random.random()
        if dup_type < 0.50:
            # exact replay (same payload, later ingest)
            pass
        elif dup_type < 0.80:
            # status correction (scheduled → completed / canceled)
            dup["status"] = random.choice([0, 1, 2])
        else:
            # duration correction (actual vs planned)
            if dup["duration"] is not None:
                dup["duration"] = max(
                    0.25,
                    dup["duration"] + random.choice([-0.5, 0.5, 1.0])
                )
        duplicate_rows.append(dup)

if duplicate_rows:
    dup_df = pd.DataFrame(duplicate_rows)
    new_sessions = pd.concat([new_sessions, dup_df], ignore_index=True)


s3 = boto3.client("s3")
BUCKET = "tutor-testprep-lakehouse"
csv_buffer = io.StringIO()

# new sessions + corruptions get ingested as a new csv
s3_path_new_sessions = f"raw/sessions/{ingest_date_folder}/new_sessions.csv"
s3.put_object(Bucket=BUCKET, Key=s3_path_new_sessions, Body=io.StringIO(new_sessions.to_csv(index=False)).getvalue())

# log changes to students facts as a delta table and write to csv
students_delta = students[students["updated"].dt.date == bd.date()].copy()
students_delta["change_type"] = np.where(
    students_delta["created"] == students_delta["updated"],
    "INSERT",
    "UPDATE")
students_delta["source_batch_id"] = f"sim_{ingest_stamp.date()}"
students_delta["ingest_ts"] = ingest_stamp + timedelta(milliseconds=random.randint(1,500))
s3_path_students_delta = f"raw/students/{ingest_date_folder}/students_delta.csv"
s3.put_object(Bucket=BUCKET, Key=s3_path_students_delta, Body=io.StringIO(students_delta.to_csv(index=False)).getvalue())


# log changes to tutors facts as a delta table and write to csv
tutors_delta = tutors[tutors["updated"].dt.date == bd.date()].copy()
tutors_delta["change_type"] = np.where(
    tutors_delta["created"] == tutors_delta["updated"],
    "INSERT",
    "UPDATE")
tutors_delta["source_batch_id"] = f"sim_{ingest_stamp.date()}"
tutors_delta["ingest_ts"] = ingest_stamp + timedelta(milliseconds=random.randint(1,500))
s3_path_tutors_delta = f"raw/tutors/{ingest_date_folder}/tutors_delta.csv"
s3.put_object(Bucket=BUCKET, Key=s3_path_tutors_delta, Body=io.StringIO(tutors_delta.to_csv(index=False)).getvalue())

# write all, flawless data to history to continue the simulation
s3.put_object(Bucket=BUCKET, Key=f"simulation/sessions.csv", Body=io.StringIO(sessions.to_csv(index=False)).getvalue())
s3.put_object(Bucket=BUCKET, Key=f"simulation/sessions_i.csv", Body=io.StringIO(sessions_i.to_csv(index=False)).getvalue())
s3.put_object(Bucket=BUCKET, Key=f"simulation/sessions_f.csv", Body=io.StringIO(sessions_f.to_csv(index=False)).getvalue())
s3.put_object(Bucket=BUCKET, Key=f"simulation/tutors.csv", Body=io.StringIO(tutors.to_csv(index=False)).getvalue())
s3.put_object(Bucket=BUCKET, Key=f"simulation/students.csv", Body=io.StringIO(students.to_csv(index=False)).getvalue())
s3.put_object(Bucket=BUCKET, Key=f"simulation/students_helpers.csv", Body=io.StringIO(students_helpers.to_csv(index=False)).getvalue())

def build_simulation_completed_event():
    return {
        "status": "SUCCESS",
        "emitted_at": datetime.now(timezone.utc).isoformat(),
        "sim_date": str(bd.date()),
        "new_sessions_count": new_sessions.shape[0],
        "students_delta_count": students_delta.shape[0],
        "tutors_delta_count": tutors_delta.shape[0]
    }

def emit_simulation_completed_event(detail: dict) -> None:
    response = events_client.put_events(
        Entries=[
            {
                "Source": "tutor.simulation",
                "DetailType": "SimulationCompleted",
                "Detail": json.dumps(detail),
                "EventBusName": "default"
            }
        ]
    )
    entry = response["Entries"][0]
    if "ErrorCode" in entry:
        raise RuntimeError(
            f"Failed to emit SimulationCompleted event: "
            f"{entry['ErrorCode']} - {entry.get('ErrorMessage')}"
        )

 

def lambda_handler(event, context):
    LOGGER.info("Starting batch simulation")
    try:

        event_detail = build_simulation_completed_event()

        emit_simulation_completed_event(event_detail)

        return event_detail

    except Exception:
        LOGGER.exception("Simulation run failed")
        raise