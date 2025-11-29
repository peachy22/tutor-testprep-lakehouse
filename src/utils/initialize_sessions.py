import csv
import random
from datetime import datetime, date, timedelta
from pathlib import Path
from initialize_students import rand_business_time
from initialize_sessions import load_csv


OUTPUT_DIR = Path("./data/gold")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "sessions.csv"


subjects = load_csv("data/gold/subjects.csv")
students = load_csv("data/gold/students.csv")
tutors = load_csv("data/gold/students.csv")


subjects_high = [subj for subj in subjects if subj["modifier"] in ["Regents","AP"]]
subjects_middle = [subj for subj in subjects if subj["modifier"] == "Grade"]
subjects_test_prep = [subj for subj in subjects if subj["modifier"] in ["SAT","ACT"]]
subjects_ultra = [subj for subj in subjects if subj["modifier"] == "IB"]


sessions = []             
first_sessions = {}       
last_sessions = {}        
quit_students = set()     


def assign_subjects():
   for stu in students:
    grade = int(stu["grade_level"])
    r = random.random()

    if grade >= 9:
        if r <= 0.60:
            bucket = subjects_test_prep
        elif r <= 0.99:   
            bucket = subjects_high
        else:             
            bucket = subjects_ultra
    else:
        if r <= 0.95:
            bucket = subjects_middle
        else:             
            bucket = subjects_high

    subject_id = random.choice(bucket)["id"]

    sessions.append({
        "student_id": stu["id"],
        "subject_id": subject_id
    })

           

def assign_first_session():
    for sesh in sessions:
       student_id = sesh["student_id"]
       student_details = next(s for s in students if s["id"] == sesh["student_id"])
       student_created = student_details["created"]
       tutor_id = random.choice([t for t in tutors if t["created"]<=student_created])["id"]
       created = datetime.strptime(student_created, "%Y-%m-%d %H:%M:%S")
       created_date = created.date()
       first_session_hour = rand_business_time(13,19).hour
       first_session_date = created_date + timedelta(days=random.randint(1,14))
       stamp = datetime(first_session_date.year, first_session_date.month, first_session_date.day, first_session_hour, 0, 0)
       sesh["tutor_id"] = tutor_id
       sesh["stamp"] = stamp
       
       first_sessions[student_id] = sesh
       last_sessions[student_id] = sesh
    
def quit(id):
    rand = random.random()
    if id in quit_students:
        return True
    elif rand < 0.05:
        quit_students.add(id)
        return True
    else:
        return False


def assign_subsequent_sessions():
    for stu in students:
        student_id = stu["id"]
        first = first_sessions.get(student_id)
        subject_id = first["subject_id"]
        tutor_id = first["tutor_id"]
        first_stamp = first["stamp"]
        while True: 
            if quit(student_id):
                break
            previous = last_sessions.get(student_id)
            previous_stamp = previous["stamp"]
            summer_cutoff = date(previous_stamp.year, 6, 15)
            duration_delta = previous_stamp-first_stamp
            duration_days = duration_delta.days
            if previous_stamp.date() > summer_cutoff and subject_id not in {s["id"] for s in subjects_test_prep}:
                break
            if duration_days > 100 and subject_id in {s["id"] for s in subjects_test_prep}:
                break
            previous_stamp_date = previous_stamp.date()
            first_sesh_hour = first_stamp.hour
            curr_sesh_hour = first_sesh_hour + random.choices([-1,0,1],[0.05,0.9,0.05],k=1)[0]
            curr_sesh_date_short = previous_stamp_date + timedelta(days=random.randint(2,4))
            curr_sesh_date_long = previous_stamp_date + timedelta(days=random.choices([6,7,8],[0.05,0.9,0.05],k=1)[0])
            rand1 = random.random()
            if rand1 <= .1:
                curr_sesh_stamp = datetime(curr_sesh_date_short.year, curr_sesh_date_short.month, curr_sesh_date_short.day, curr_sesh_hour, 0, 0)
            else:
                curr_sesh_stamp = datetime(curr_sesh_date_long.year, curr_sesh_date_long.month, curr_sesh_date_long.day, curr_sesh_hour, 0, 0)
            last_sessions["stamp"] = curr_sesh_stamp
            rand2 = random.random()
            if rand2 <= .2:
                continue
            else:
                sessions.append({
                 "student_id": student_id,
                 "subject_id": subject_id,
                 "tutor_id": tutor_id,
                 "stamp": curr_sesh_stamp
                   })
    
        


def write_sessions_csv(rows):
    header = [
        "student_id","subject_id","tutor_id","stamp"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} sessions in: {OUTPUT_FILE}")


def generate_sessions():
    assign_subjects()
    assign_first_session()
    assign_subsequent_sessions()
    return sessions

generate_sessions()

if __name__ == "__main__":
     write_sessions_csv(sessions)
















