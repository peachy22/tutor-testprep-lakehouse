import pandas as pd
from datetime import datetime, date, timedelta
from lists import GIRL_NAMES, BOY_NAMES, LAST_NAMES
import random
import os

# declare start date and number of students for the first tutor in week 1
students_week_1 = 28
sim_start = datetime(2021,8,24,0,0,0)
# this is the date at which the historical sim will end, after which daily batch loads will occur
hist_cutoff = datetime(2025,12,20,0,0,0) 
# some growth behaviors will be bound to the progress towards this date
sim_end = datetime(2027,12,31,0,0,0)

# function for simulating week 1 and the first group of students
def week_1(sim_start,sim_end,students_week_1):
    tutors.loc[len(tutors)] = [0,'Stephan','Pichardo','M',date(1993,10,30),0,0,sim_start,sim_start]
    tutor_count = 1
    student_count = 0
    active_student_count = 0
    session_count = 0
    # create profiles for initial student load
    while student_count < students_week_1:
        #25% probability student's grade is 6-8, 75% between 9-12
        grade_level = random.choices([random.choice(range(6,8)),random.choice(range(9,12))],[.25,.75],k=1)[0]
        #age roughly based on grade
        age = grade_level + 6
        dob = (sim_start + timedelta(days = random.randint(-365,365))) - timedelta(days=365*age)
        sex = random.choices(['M','F'],[.39,.61],k=1)[0]
        if sex == 'M':
            first_name = random.choice(BOY_NAMES)
        else:
            first_name = random.choice(GIRL_NAMES)
        last_name = random.choice(LAST_NAMES)
        #initial contract per hour is $80
        rate = 80
        students.loc[len(students)] = [student_count,first_name,last_name,sex,dob.date(),grade_level,"Active",rate,sim_start,sim_start]
        #student's school year ends at some point in May or June
        students_helpers.loc[len(students_helpers)] = [student_count,random.choice([5,6]),random.choice(range(1,30)),1,9]
        #increment active students for the tutor, the active student count overall, and the total student count for id
        tutors.loc[tutors["tutor_id"] == 0, "active_students"] += 1
        student_count += 1
        active_student_count += 1
    #create sessions for week 1 students
    for idx, row in students.iterrows():
        tutor_id = 0
        #business hours are after school; 1pm - 7pm
        first_session_hour = random.choice(range(13,19))
        #most students are math and SAT/ACT, and stick with that subject for their tenure at the center
        subject_id = random.choices([1,2,random.choice([3,4]),random.choice([5,6])],[.3,.4,.2,.1],k=1)[0]
        stamp = datetime(sim_start.year, sim_start.month, random.choice(range(sim_start.date().day,sim_start.date().day+6)), first_session_hour, 0, 0)
        duration = random.choices([1,1.5,2],[.9,.05,.05],k=1)[0]
        sessions.loc[len(sessions)] = [session_count,row["student_id"],tutor_id,subject_id,stamp,duration,0]
        sessions_i.loc[len(sessions_i)] = [session_count,row["student_id"],tutor_id,subject_id,stamp,duration,0]
        sessions_f.loc[len(sessions_f)] = [session_count,row["student_id"],tutor_id,subject_id,stamp,duration,0]
        #increment session count for id
        session_count = session_count + 1
    return student_count, active_student_count, session_count, tutor_count, sim_start, sim_end

# function for creating new students as business days occur
def create_new_student(business_day,new_student_multiplier,student_count, active_student_count):
    i = 1
    #sometimes later on in the simulation, multiple students will sign up in one day
    while i <= new_student_multiplier: 
        grade_level = random.choices([random.choice(range(6,8)),random.choice(range(9,12))],[.25,.75],k=1)[0]
        first_session_hour = random.choice(range(13,19))
        created = datetime(business_day.year, business_day.month, business_day.day, first_session_hour, 0, 0)
        age = grade_level + 6
        birth_year = business_day.year - age
        dob = datetime(birth_year,random.randint(1, 12),random.randint(1, 28))
        sex = random.choices(['M','F'],[.39,.61],k=1)[0]
        #the price for new students will rise as the business grows
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

# function for hiring new tutors as session load increases
def create_new_tutor(tutor_count):
    tutor_id = tutor_count
    age = random.choice([20,50])
    # contractors have different rates depending on experience
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
    # increment tutor count for IDs
    tutor_count += 1
    return tutor_id, tutor_count

# function for the random churn and onboarding of clients each day
def stochastic_churn(business_day, sim_start, sim_end, season):
    # as time progresses and the business matures, probabilities associated with new students rise
    progress = (business_day - sim_start).days / (sim_end - sim_start).days
    progress = max(0, min(1, progress))  
    # in the fall, the chance for new signups can increase a lot
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
    # students have a certain chance of quitting for various reasons each time they have a scheduled session
    base_churn = 0.0044
    churn_noise = random.uniform(0.8, 1.2)
    stochastic_churn_prob = base_churn * churn_noise
    # when all tutors have this number of students, a new one will be hired
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
            # increment the number of sessions for id and the cleint load for the selected tutor
            tutors.loc[tutors["tutor_id"] == tutor_id, "active_students"] += 1
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
            duration_delta = last_session_date-first_session_date
            duration_days = duration_delta.days
            subject_id = first_session["subject_id"].iloc[0]
            tutor_id = first_session["tutor_id"].iloc[0]
            # students have a session once per week. If it has been a week since their last session:
            if (curr_session_date-last_session_date).days == 7:
                # the student will quit if they hit the random churn threshold, if they are an SAT student and they have prepped for enough time, or if their school year is over (they can return next year)
                if random.random() < stochastic_churn_prob or (duration_days > 120 and subject_id == 1) or (last_session_date > date(curr_session_year,summer_cutoff_month,summer_cutoff_day) and subject_id != 1):
                    students.loc[students["student_id"] == student_id, "status"] = 'Inactive'
                    students.loc[students["student_id"] == student_id, "updated"] = business_day
                    # the student is returnable if they were studying standard school work and quit at the end of their school year
                    if (last_session_date > date(curr_session_year,summer_cutoff_month,summer_cutoff_day) and subject_id != 1):
                        students_helpers.loc[students_helpers["student_id"] == student_id, "returnable"] = 1
                    else:
                        students_helpers.loc[students_helpers["student_id"] == student_id, "returnable"] = 0
                    # decrement the student load to free up the tutor
                    tutors.loc[tutors["tutor_id"] == tutor_id, "active_students"] -= 1
                    active_student_count -= 1
                # the student will have a session, or a cancelled session, if they do not quit
                else:
                    last_session_hour = last_session["stamp"].iloc[0].hour
                    # the student's session time is roughly the same as their last one
                    curr_session_hour = first_session_hour + random.choices([0,-1,1],[.8,.1,.1],k=1)[0]
                    duration = last_session["duration"].iloc[0]
                    stamp = datetime(curr_session_date.year, curr_session_date.month, curr_session_date.day, curr_session_hour, 0, 0)
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
            session_count += 1
            active_student_count += 1
            continue
    return tutor_count, student_count, active_student_count, session_count

# function for creating date loop after week 1
def daterange(start_date: date, end_date: date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(days=n)

if __name__ == "__main__":



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

    # non-operational student data for simulation propoerties
    students_helpers = pd.DataFrame({'student_id':[],
                         'summer_cutoff_month':[],
                         'summer_cutoff_day':[],
                         'returnable':[],
                         'school_year_start_month':[]})

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

    # possible subjects; k-12
    subjects = pd.DataFrame({'subject_id':[1,2,3,4,5,6],
                         'name':['SAT/ACT','Math','Chemistry','Physics','Language Arts','Social Studies']})

    # first session for each student, per active period
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

# tutor 0 hosts sessions during the first week in the center
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

# write clean pre-migration history to raw; the center migrates to AWS and a new CRM after the cutoff
    ingest_date = max(sessions_f["stamp"]).date() + timedelta(days=1)
    ingest_date_folder = f"ingest_date={ingest_date.strftime('%Y-%m-%d')}"

    os.makedirs(f"data/raw/students/{ingest_date_folder}", exist_ok=True)
    students_path = f"data/raw/students/{ingest_date_folder}/students.csv"
    students.to_csv(students_path, index=False)
    
    os.makedirs(f"data/raw/sessions/{ingest_date_folder}", exist_ok=True)
    sessions_path = f"data/raw/sessions/{ingest_date_folder}/sessions.csv"
    sessions.to_csv(sessions_path, index=False)

    os.makedirs(f"data/raw/tutors/{ingest_date_folder}", exist_ok=True)
    tutors_path = f"data/raw/tutors/{ingest_date_folder}/tutors.csv"
    tutors.to_csv(tutors_path, index=False)








