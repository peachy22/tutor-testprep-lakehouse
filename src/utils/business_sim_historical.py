import pandas as pd
from datetime import datetime, date, timedelta
from lists import GIRL_NAMES, BOY_NAMES, LAST_NAMES
import random
import os

# declare start date, end date, and number of students for the first tutor in week 1

sim_start = datetime(2020,8,23,0,0,1)
sim_end = datetime(2027,12,31,0,0,0)
hist_cutoff = datetime(2025,12,19,0,0,0)
students_week_1 = 10


# create simulation functions

    # function for simulating week 1 and the first group of students
def week_1(sim_start,sim_end,students_week_1):
    tutors.loc[len(tutors)] = [0,'Stephan','Pichardo','M',date(1993,10,30),0,0,sim_start,sim_start]
    tutor_count = 1
    student_count = 0
    active_student_count = 0
    session_count = 0
    while student_count < students_week_1:
        grade_level = random.choices([random.choice(range(6,8)),random.choice(range(9,12))],[.25,.75],k=1)[0]
        age = grade_level + 6
        dob = (sim_start + timedelta(days = random.randint(-365,365))) - timedelta(days=365*age)
        sex = random.choices(['M','F'],[.39,.61],k=1)[0]
        if sex == 'M':
            first_name = random.choice(BOY_NAMES)
        else:
            first_name = random.choice(GIRL_NAMES)
        last_name = random.choice(LAST_NAMES)
        students.loc[len(students)] = [student_count,first_name,last_name,sex,dob.date(),grade_level,"Active",80,sim_start,sim_start]
        students_helpers.loc[len(students_helpers)] = [student_count,random.choice([5,6]),random.choice(range(1,30)),1]
        tutors.loc[tutors["tutor_id"] == 0, "active_students"] += 1
        student_count += 1
        active_student_count += 1
    for idx, row in students.iterrows():
        tutor_id = 0
        first_session_hour = random.choice(range(13,19))
        subject_id = random.choices([1,2,random.choice([3,4]),random.choice([5,6])],[.3,.4,.2,.1],k=1)[0]
        stamp = datetime(sim_start.year, sim_start.month, random.choice(range(sim_start.date().day,sim_start.date().day+6)), first_session_hour, 0, 0)
        duration = random.choices([1,1.5,2],[.9,.05,.05],k=1)[0]
        sessions.loc[len(sessions)] = [session_count,row["student_id"],tutor_id,subject_id,stamp,duration,0]
        sessions_i.loc[len(sessions_i)] = [session_count,row["student_id"],tutor_id,subject_id,stamp,duration,0]
        sessions_f.loc[len(sessions_f)] = [session_count,row["student_id"],tutor_id,subject_id,stamp,duration,0]
        session_count = session_count + 1
    return student_count, active_student_count, session_count, tutor_count, sim_start, sim_end

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

    # function for creating loopable date boundaries after week 1
def daterange(start_date: date, end_date: date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(days=n)

if __name__ == "__main__":

    # initialize dataframes

    # students
    students = pd.DataFrame({'student_id':[],
                         'first_name':[],
                         'last_name':[],
                         'sex':[],
                         'date_of_birth':[],
                         'grade':[],
                         'status':[],
                         'contract_rate':[],
                         'created':[],
                         'updated':[]})

    students_helpers = pd.DataFrame({'student_id':[],
                         'summer_cutoff_month':[],
                         'summer_cutoff_day':[],
                         'returnable':[]})

    #tutors
    tutors = pd.DataFrame({'tutor_id':[],
                       'first_name':[],
                       'last_name':[],
                       'sex':[],
                       'date_of_birth':[],
                       'contract_rate':[],
                       'active_students':[],
                       'created':[],
                       'updated':[]})

    # sessions completed
    sessions = pd.DataFrame({'session_id':[],
                         'student_id':[],
                         'tutor_id':[],
                         'subject_id': [],
                         'stamp':[],
                         'duration':[],
                         'status':[]})

    # possible subjects
    subjects = pd.DataFrame({'subject_id':[1,2,3,4,5,6],
                         'name':['SAT/ACT','Math','Chemistry','Physics','Language Arts','Social Studies']})

    # first session for each student
    sessions_i = pd.DataFrame({'session_id':[],
                         'student_id':[],
                         'tutor_id':[],
                         'subject_id': [],
                         'stamp':[],
                         'duration':[],
                         'status':[]})

    # most recent session for each student
    sessions_f = pd.DataFrame({'session_id':[],
                         'student_id':[],
                         'tutor_id':[],
                         'subject_id': [],
                         'stamp':[],
                         'duration':[],
                         'status':[]})

# tutor 0 (the founder) has sessions during the first week in the center
    student_count, active_student_count, session_count, tutor_count, sim_start, sim_end = week_1(sim_start, sim_end, students_week_1)

# subsequent business days occur after week 1, growing the active student and the tutor count as needed
    for d in daterange(sim_start + timedelta(days=7), hist_cutoff):
        tutor_count, student_count, active_student_count, session_count = create_sessions(d, tutor_count, student_count, active_student_count, session_count, sim_start, sim_end)

# write clean simulation history to utils for continuity on subsequent sim runs post-migration
    sessions.to_csv('src/simulation/sessions.csv', index=False)
    students.to_csv('src/simulation/students.csv', index=False)
    tutors.to_csv('src/simulation/tutors.csv', index=False)
    sessions_i.to_csv('src/simulation/sessions_i.csv', index=False)
    sessions_f.to_csv('src/simulation/sessions_f.csv', index=False)
    students_helpers.to_csv('src/simulation/students_helpers.csv', index=False)

# write clean pre-migration history to raw
    ingest_date_folder = f"ingest_date={hist_cutoff.strftime('%Y-%m-%d')}"

    os.makedirs(f"data/raw/students/{ingest_date_folder}", exist_ok=True)
    students_path = f"data/raw/students/{ingest_date_folder}/students.csv"
    students.to_csv(students_path, index=False)
    
    os.makedirs(f"data/raw/sessions/{ingest_date_folder}", exist_ok=True)
    sessions_path = f"data/raw/sessions/{ingest_date_folder}/sessions.csv"
    sessions.to_csv(sessions_path, index=False)

    os.makedirs(f"data/raw/tutors/{ingest_date_folder}", exist_ok=True)
    tutors_path = f"data/raw/tutors/{ingest_date_folder}/tutors.csv"
    tutors.to_csv(tutors_path, index=False)








