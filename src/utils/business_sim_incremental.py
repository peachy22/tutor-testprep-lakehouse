import pandas as pd
import numpy as np
import os
from datetime import datetime, date, timedelta
from lists import GIRL_NAMES, BOY_NAMES, LAST_NAMES
from business_sim_historical import sim_start, sim_end, hist_cutoff
import random

students = pd.read_csv('src/simulation/students.csv')
students_helpers = pd.read_csv('src/simulation/students_helpers.csv')
tutors = pd.read_csv('src/simulation/tutors.csv')
sessions = pd.read_csv('src/simulation/sessions.csv')
sessions_i = pd.read_csv('src/simulation/sessions_i.csv')
sessions_f = pd.read_csv('src/simulation/sessions_f.csv')

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

    # function for creating new students as business days occur
def create_new_student(business_day,new_student_multiplier,student_count, active_student_count):
    i = 1
    while i <= new_student_multiplier:
        grade_level = random.choices([random.choice(range(6,8)),random.choice(range(9,12))],[.25,.75],k=1)[0]
        first_session_hour = random.choice(range(13,19))
        created = datetime(business_day.year, business_day.month, business_day.day, first_session_hour, 0, 0)
        age = grade_level + 6
        dob = (business_day + timedelta(days = random.randint(-365,365))) - timedelta(days=365*age)
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
        students_helpers.loc[len(students_helpers)] = [student_count,random.choice([5,6]),random.choice(range(1,30)),0]
        i = i + 1
        student_count += 1
        active_student_count += 1
    return student_count, active_student_count

  # function for creating new students as business days occur
def create_new_student(business_day,new_student_multiplier,student_count, active_student_count):
    i = 1
    while i <= new_student_multiplier:
        grade_level = random.choices([random.choice(range(6,8)),random.choice(range(9,12))],[.25,.75],k=1)[0]
        first_session_hour = random.choice(range(13,19))
        created = datetime(business_day.year, business_day.month, business_day.day, first_session_hour, 0, 0)
        age = grade_level + 6
        dob = (business_day + timedelta(days = random.randint(-365,365))) - timedelta(days=365*age)
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
        students_helpers.loc[len(students_helpers)] = [student_count,random.choice([5,6]),random.choice(range(1,30)),0]
        i = i + 1
        student_count += 1
        active_student_count += 1
    return student_count, active_student_count

    # function for hiring new tutors as session load increases
def create_new_tutor(tutor_count):
    tutor_id = tutor_count
    age = random.choice([20,50])
    contract = random.choice([30,35,40,45,50])
    sex = random.choice(['M','F'])
    if sex == 'M':
        first_name = random.choice(BOY_NAMES)
    else:
        first_name = random.choice(GIRL_NAMES)
    last_name = random.choice(LAST_NAMES)
    dob = (datetime.today() + timedelta(days = random.randint(-365,365))) - timedelta(days=365*age)
    created = max(students["created"])
    tutors.loc[len(tutors)] = [tutor_id, first_name, last_name, sex, dob.date(), contract, 0, created, created]
    tutor_count += 1
    return tutor_id, tutor_count

    # function for the random churn and onboarding of clients each day
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
    mult_noise = random.uniform(0.9, 1.1)  
    new_student_multiplier = base_mult * mult_noise
    new_student_multiplier = max(1, new_student_multiplier)
    base_churn = 0.0044
    churn_noise = random.uniform(0.8, 1.2)
    stochastic_churn_prob = base_churn * churn_noise
    student_tutor_ratio = 30
    return new_student_prob, new_student_multiplier, student_tutor_ratio, stochastic_churn_prob

    # function for simulating new sessions and triggering the creation of new students and tutors
def create_sessions(business_day, tutor_count, student_count, active_student_count, session_count, sim_start, sim_end):
    month = business_day.month
    if month in [9,10,11]:
        season = 'fall'
    elif month in [1,2,3,4,5,12]:
        season = 'spring'
    else:
        season = 'summer'
    new_student_prob, new_student_multiplier, student_tutor_ratio, stochastic_churn_prob = stochastic_churn(business_day, sim_start, sim_end, season)
    if random.random() < new_student_prob:
        student_count, active_student_count = create_new_student(business_day,new_student_multiplier,student_count, active_student_count)
    for idx, row in students.iterrows():
        student_id = row["student_id"]
        student_helper = students_helpers[students_helpers["student_id"] == student_id]
        student_is_returnable = student_helper["returnable"].iloc[0]
        summer_cutoff_month = student_helper["summer_cutoff_month"].iloc[0]
        summer_cutoff_day = student_helper["summer_cutoff_day"].iloc[0]
        if student_id not in sessions_i["student_id"].values:
            eligible = tutors.loc[tutors["active_students"] < student_tutor_ratio, "tutor_id"].tolist()
            if eligible:
                tutor_id = random.choice(eligible)
            else:
                tutor_id, tutor_count = create_new_tutor(tutor_count)
            subject_id = random.choices([1,2,random.choice([3,4]),random.choice([5,6])],[.3,.4,.2,.1],k=1)[0]
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
            tutors.loc[tutors["tutor_id"] == tutor_id, "active_students"] += 1
            session_count += 1
            continue
        elif row["status"] == "Active":
            first_session = sessions_i[sessions_i["student_id"] == student_id]
            first_session_date = first_session["stamp"].iloc[0].date()
            last_session = sessions_f[sessions_f["student_id"] == student_id]
            last_session_date = last_session["stamp"].iloc[0].date()
            curr_session_date = business_day.date()
            curr_session_year = business_day.year
            duration_delta = last_session_date-first_session_date
            duration_days = duration_delta.days
            subject_id = first_session["subject_id"].iloc[0]
            tutor_id = first_session["tutor_id"].iloc[0]
            if (curr_session_date-last_session_date).days == 7:
                if random.random() < stochastic_churn_prob or (duration_days > 120 and subject_id == 1) or (last_session_date > date(curr_session_year,summer_cutoff_month,summer_cutoff_day) and subject_id != 1):
                    students.loc[students["student_id"] == student_id, "status"] = 'Inactive'
                    students.loc[students["student_id"] == student_id, "updated"] = business_day
                    if (last_session_date > date(curr_session_year,summer_cutoff_month,summer_cutoff_day) and subject_id != 1):
                        students_helpers.loc[students_helpers["student_id"] == student_id, "returnable"] = 1
                    tutors.loc[tutors["tutor_id"] == tutor_id, "active_students"] -= 1
                    active_student_count -= 1
                else:
                    last_session_hour = last_session["stamp"].iloc[0].hour
                    curr_session_hour = last_session_hour
                    duration = last_session["duration"].iloc[0]
                    stamp = datetime(curr_session_date.year, curr_session_date.month, curr_session_date.day, curr_session_hour, 0, 0)
                    status = random.choices([0,1,2],[.75,.15,.10],k=1)[0]
                    sessions.loc[len(sessions)] = [session_count,student_id,tutor_id,subject_id,stamp,duration,status]
                    sessions_f.loc[sessions_f["student_id"] == student_id] = [session_count,student_id,tutor_id,subject_id,stamp,duration,status]
                    session_count += 1
        elif row["status"] == "Inactive" and row["grade"] < 12 and student_is_returnable == 1 and ((business_day.month == 9 and random.random() < 0.04) or (business_day.month == 10 and random.random() < 0.03) or (business_day.month == 11 and random.random() < 0.02) or (business_day.month == 12 and random.random() < 0.01)):
            students.loc[students["student_id"] == student_id, "status"] = 'Active'
            students.loc[students["student_id"] == student_id, "grade"] += 1
            students.loc[students["student_id"] == student_id, "updated"] = business_day
            last_session = sessions_f[sessions_f["student_id"] == student_id]
            last_tutor = last_session["tutor_id"].iloc[0]
            preferred_tutor = tutors.loc[(tutors["active_students"] < student_tutor_ratio + 8) & (tutors["tutor_id"] == last_tutor), "tutor_id"].tolist()
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
            sessions_f.loc[len(sessions_f)] = [session_count,student_id,tutor_id,subject_id,stamp,duration,0]
            tutors.loc[tutors["tutor_id"] == tutor_id, "active_students"] += 1
            session_count += 1
            active_student_count += 1
    return tutor_count, student_count, active_student_count, session_count


def daterange(start_date: date, end_date: date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(days=n)

inc_hist_start = max(sessions_f["stamp"]).date() + timedelta(days=1)
inc_hist_end   = date(2025, 10, 12)

for d in daterange(inc_hist_start, inc_hist_end):
    last_datetime = max(sessions_f['stamp']) + timedelta(days = 1)
    bd = last_datetime - timedelta(hours=last_datetime.hour)
    ingest_date_folder = f"ingest_date={bd.strftime('%Y-%m-%d')}"

    tutor_count, student_count, active_student_count, session_count = create_sessions(bd, tutor_count, student_count, active_student_count, session_count, sim_start, sim_end)

    new_sessions = sessions[sessions["stamp"].dt.date == bd.date()].copy()
    new_sessions["source_batch_id"] = f"sim_{bd.date():%Y%m%d}"
    batch_ingest_time = datetime.utcnow()
    new_sessions["ingest_ts"] = batch_ingest_time

    duplicate_rows = []
    for idx, row in new_sessions.iterrows():
        stamp = row["stamp"]
        if random.random() < .03: # 3% durations go from hours to minutes
            new_sessions.loc[idx, "duration"] *= 60
        if random.random() < .01: # 1% sessions get emitted for a previous day
            new_sessions.loc[idx, "stamp"] = stamp + timedelta(days = -random.randint(1,30))
        if random.random() < .005: # .5% sessions get emitted for a future day
            new_sessions.loc[idx, "stamp"] = stamp + timedelta(days = 30)
        if random.random() < .05: # 5% null duration
            new_sessions.loc[idx, "duration"] = None
        if random.random() < .03: # 3% null status
            new_sessions.loc[idx, "status"] = None
        if random.random() < .03: # 3% null tutor_id
            new_sessions.loc[idx, "tutor_id"] = None
        if random.random() < .01: # 1% null stamp
            new_sessions.loc[idx, "stamp"] = None
        if random.random() < 0.03: # 3% duplicate session
            dup = row.copy()
            dup["ingest_ts"] = batch_ingest_time + timedelta(milliseconds=random.randint(1,500))
            duplicate_rows.append(dup)

    if duplicate_rows:
        dup_df = pd.DataFrame(duplicate_rows)
        new_sessions = pd.concat([new_sessions, dup_df], ignore_index=True)

    os.makedirs(f"data/raw/sessions/{ingest_date_folder}", exist_ok=True)
    new_sessions_path = f"data/raw/sessions/{ingest_date_folder}/new_sessions.csv"
    new_sessions.to_csv(new_sessions_path, index=False)

    students_delta = students[students["updated"].dt.date == bd.date()].copy()
    students_delta["change_type"] = np.where(
        students_delta["created"] == students_delta["updated"],
        "INSERT",
        "UPDATE")
    os.makedirs(f"data/raw/students/{ingest_date_folder}", exist_ok=True)
    students_delta_path = f"data/raw/students/{ingest_date_folder}/students_delta.csv"
    students_delta.to_csv(students_delta_path, index=False)


    tutors_delta = tutors[tutors["updated"].dt.date == bd.date()].copy()
    tutors_delta["change_type"] = np.where(
        tutors_delta["created"] == tutors_delta["updated"],
        "INSERT",
        "UPDATE")
    os.makedirs(f"data/raw/tutors/{ingest_date_folder}", exist_ok=True)
    tutors_delta_path = f"data/raw/tutors/{ingest_date_folder}/tutors_delta.csv"
    tutors_delta.to_csv(tutors_delta_path, index=False)


    sessions.to_csv('src/simulation/sessions.csv', index=False)
    students.to_csv('src/simulation/students.csv', index=False)
    tutors.to_csv('src/usimulation/tutors.csv', index=False)
    sessions_i.to_csv('src/simulation/sessions_i.csv', index=False)
    sessions_f.to_csv('src/simulation/sessions_f.csv', index=False)
    students_helpers.to_csv('src/simulation/students_helpers.csv', index=False)


