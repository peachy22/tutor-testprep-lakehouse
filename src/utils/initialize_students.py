import csv
import random
from pathlib import Path
from datetime import date, time, datetime, timedelta


NUM_STUDENTS = 1000

OUTPUT_DIR = Path("./data/gold")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "students.csv"

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

STREETS = [
    "Maple", "Cedar", "Oakwood", "Pinecrest", "Willow",
    "Broadway", "Elm", "Hillside", "Ridgeway", "Valley View",
    "Lakewood", "Sunset", "Forest Glen", "Riverview", "Meadowbrook",
    "Highland", "Sycamore", "Birchwood", "Lincoln", "Jefferson",
    "Madison", "Washington", "Chestnut", "Laurel", "Summit",
    "Aspen", "Spruce", "Riverbend", "Parkview", "Garden Grove",
    "Westfield", "Eastgate", "Southridge", "Northwood", "Creekside",
    "Fairview", "Heritage", "Stonebridge", "Prairie View", "Horizon",
    "Bayshore", "Harbor View", "Greenfield", "Wildflower", "Canyon Ridge",
    "Silver Oak", "Timberline", "Whispering Pines", "Golden Meadow", "Meadow Ridge"
]

STREET_SUFFIXES = [
    "Street", "Avenue", "Road", "Drive", "Lane",
    "Court", "Place", "Boulevard", "Parkway", "Way",
    "Terrace", "Circle", "Trail", "Highway", "Loop"
]

ZIP_CODES_NASSAU = [
    11001, 11002, 11003, 11004, 11005,
    11010, 11020, 11021, 11022, 11023,
    11024, 11026, 11027, 11030, 11040,
    11041, 11042, 11050, 11051, 11052,
    11053, 11054, 11055, 11096, 11742,
    11501, 11507, 11509, 11510, 11514,
    11516, 11518, 11520, 11530, 11542,
    11545, 11547, 11548, 11549, 11550,
    11551, 11552, 11553, 11554, 11556,
    11557, 11558, 11559, 11560, 11561,
    11563, 11565, 11566, 11568, 11569,
    11570, 11572, 11575, 11576, 11577,
    11579, 11580, 11581, 11582, 11590,
    11596, 11598
]

ZIP_CODES_SUFFOLK = [
    11701, 11702, 11703, 11704, 11705,
    11706, 11707, 11708, 11709, 11710,
    11713, 11715, 11716, 11717, 11718,
    11719, 11720, 11721, 11722, 11724,
    11725, 11726, 11727, 11729, 11730,
    11731, 11732, 11733, 11735, 11738,
    11739, 11740, 11741, 11742, 11743,
    11746, 11747, 11749, 11750, 11751,
    11752, 11754, 11755, 11757, 11758,
    11760, 11763, 11764, 11765, 11766,
    11767, 11768, 11769, 11770, 11772,
    11775, 11776, 11777, 11778, 11779,
    11780, 11782, 11784, 11786, 11787,
    11788, 11789, 11790, 11792, 11794,
    11795, 11796, 11797, 11798, 11742,
    11901, 11930, 11931, 11932, 11933,
    11934, 11935, 11937, 11939, 11940,
    11941, 11942, 11944, 11946, 11947,
    11948, 11949, 11950, 11951, 11952,
    11953, 11954, 11955, 11956, 11957,
    11958, 11959, 11960, 11961, 11962,
    11963, 11964, 11965, 11967, 11968,
    11969, 11970, 11971, 11972, 11973,
    11975, 11976, 11977, 11978
]


# ---------------------------------------
# Helpers
# ---------------------------------------

def rand_business_time(start_hour=8,end_hour=19):
    start_seconds = start_hour * 3600
    end_seconds = end_hour * 3600
    random_seconds = random.randint(start_seconds, end_seconds - 1)
    hours = random_seconds // 3600
    minutes = (random_seconds % 3600) // 60
    seconds = random_seconds % 60
    return time(hours, minutes, seconds)

def rand_created(student_id, start_year=2016, jitter = 10):
    start = date(start_year, 1, 1)
    today = date.today()
    total_days = (today - start).days
    x = student_id / NUM_STUDENTS
    position = 1 - x ** 1.3
    base = start + timedelta(days=int(total_days * position))
    jitter_days = random.randint(-jitter, jitter)
    created = base + timedelta(days=jitter_days)
    if created.month in {6, 7, 8}:
        direction = random.choices(["forward", "neutral"], weights=[0.7, 0.3], k=1)[0]
        if direction == "forward":
            created = date(created.year, 9, 1) + timedelta(days=random.randint(-30, 60))
        else:
            created = created
    created = f"{created}{" "}{rand_business_time()}"
    created = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
    return created



# def date_of_birth_error(d):
#     return random.choice([
#         d.isoformat(),
#         d.strftime("%m/%d/%Y"),
#         d.strftime("%m-%d-%Y"),
#         d.strftime("%Y%m%d")
#                      ])

def rand_date_of_birth(grade_level,created):
    created = created.date()
    age = random.randint(grade_level+5, grade_level+7)
    days_old = age * 365 + random.randint(0, 364)
    dob = created - timedelta(days=days_old)
    return dob

# def first_name_error(f):
#     return random.choice([
#             f"{f}{' '}",
#             f"{' '}{f}",
#             f.upper()
#         ]
#         )

def rand_first_name(type, sex = ""):
    if type == 'S':
        if sex == 'M': first = random.choice(BOY_NAMES)
        elif sex == 'F': first = random.choice(GIRL_NAMES)
        else: first = random.choice(BOY_NAMES+GIRL_NAMES)
    elif type == 'G':
        first = random.choice(BOY_NAMES+GIRL_NAMES)
    # if random.random() < 0.03 and first != None:
    #     first = first_name_error(first)
    return first

# def last_name_error(ln,sex):
#     if sex == 'M':
#         ln = random.choice([
#             f"{ln}{' '}",
#             f"{' '}{ln}",
#             f"{ln}{" Jr"}",
#             f"{ln}{" jr"}",
#             ln.upper()
#         ])
#     else:
#         ln = random.choice([
#             f"{ln}{' '}",
#             f"{' '}{ln}",
#             ln.upper()
#         ]
#         )
#     return ln

def rand_last_name(sex):
    last = random.choice(LAST_NAMES)
    # if random.random() < 0.03:
    #     last = last_name_error(last, sex)
    return last

# def email_error(em):
#     em = random.choice([
#             em.replace('@','@@'),
#             em.replace('@',''),
#             em.replace('.com','.co'),
#             em.replace('.com','com'),
#             f"{em}{' '}",
#             f"{' '}{em}",
#             em.upper()
#         ]
#         )
#     return em

def rand_email(type,first, last, domain="somedomain.com"):
    a = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{domain}"
    # if type == 'S':
    #     address = random.choices(population=[None,a],weights = [.75,.25],k=1)[0]
    # elif type == 'G':
    #     address = random.choices(population=[None,a],weights = [.1,.9],k=1)[0]
    # if random.random() < 0.03 and address != None:
    #     address = email_error(address)
    return a

# def phone_error(pn):
#     pn = random.choice([
#         pn.replace("-",""),
#         f"{"+1-"}{pn}",
#         f"{+1}{pn.replace("-","")}"
#         ])
#     return pn

def rand_phone(type):
    a = random.randint(200, 999)
    b = random.randint(200, 999)
    c = random.randint(1000, 9999)
    n = f"{a}-{b}-{c}"
    # if type == 'S':
    #     n = random.choices(population=[None,n],weights = [.6,.4],k=1)[0]
    # elif type == 'G':
    #     n = random.choices(population=[None,n],weights = [.03,.97],k=1)[0]
    # if random.random() < 0.03 and n != None:
    #     n = phone_error(n)
    return n

def rand_address():
    a = f"{random.randint(1,999)}{" "}{random.choice(STREETS)}{" "}{random.choice(STREET_SUFFIXES)}{" "}{random.choices([random.choice(ZIP_CODES_NASSAU),random.choice(ZIP_CODES_SUFFOLK)],[.7,.3],k=1)[0]}"
    return a

# def rand_disp_grade_level(gl):
#     if random.random() < 0.05:
#         if gl == 3: gl = random.choice(["3rd grade", "grade 3"])
#         if gl == 4: gl = random.choice(["4th grade", "grade 4"])
#         if gl == 5: gl = random.choice(["5th grade","grade 5"])
#         if gl == 6: gl = random.choice(["6th grade", "grade 6"])
#         if gl == 7: gl = random.choice(["7th grade", "Grade 7"])
#         if gl == 8: gl = random.choice(["8th grade", "grade 8"])
#         if gl == 9: gl = random.choice(["freshman"])
#         if gl == 10: gl = random.choice(["sophomore"])
#         if gl == 11: gl = random.choice(["junior"])
#         if gl == 12: gl = random.choice(["senior"])
#     else:
#         gl = gl
#     return gl

# ---------------------------------------
# Main student generator
# ---------------------------------------

def generate_students(num_students=NUM_STUDENTS):
    rows = []

    for student_id in range(1, num_students + 1):

        created = rand_created(student_id)
        updated = created

        sex = random.choices(population = ['M','F','X'], weights = [0.45,0.54,0.01], k=1)[0]
        student_first = rand_first_name('S',sex)
        guardian_first = rand_first_name('G')
        last = rand_last_name(sex)
        student_email = rand_email('S',student_first,last)
        guardian_email = rand_email('G',guardian_first,last)
        student_phone = rand_phone('S')
        guardian_phone = rand_phone('G')
        grade_level = random.choices([random.choice([3,4,5,6,7]),random.choice([8,9,10,11,12])],[.22,.78],k=1)[0]
        date_of_birth = rand_date_of_birth(grade_level,created)
        contact_address = rand_address()
        rows.append({
            "id": student_id,
            "student_first_name": student_first,
            "student_last_name": last,
            "date_of_birth": date_of_birth,
            "gender": sex,
            "grade_level": grade_level,
            "student_email": student_email,
            "student_phone": student_phone,
            "contact_address": contact_address,
            "guardian_first_name": guardian_first,
            "guardian_last_name": last,
            "guardian_email": guardian_email,
            "guardian_phone": guardian_phone,
            "created": created,
            "updated": updated,
        })

    return rows

# def maybe_duplicate_student(student, prob=0.03):
#     if random.random() > prob:
#         return None
#     dup = student.copy()
#     if dup.get("student_first_name") and random.random() < 0.30:
#         dup["student_first_name"] = first_name_error(dup["student_first_name"])
#     if dup.get("student_last_name") and random.random() < 0.30:
#         dup["student_last_name"] = last_name_error(dup["student_last_name"],dup["gender"])
#     if dup.get("student_phone") and random.random() < 0.30:
#         dup["student_phone"] = phone_error(dup["student_phone"])
#     if dup.get("guardian_phone") and random.random() < 0.30:
#         dup["guardian_phone"] = phone_error(dup["guardian_phone"])
#     if dup.get("student_email") and random.random() < 0.30:
#         dup["student_email"] = email_error(dup["student_email"])
#     if dup.get("guardian_email") and random.random() < 0.30:
#         dup["guardian_email"] = email_error(dup["guardian_email"])
#     dup["created"] = dup["created"] + timedelta(days=random.randint(-30, 30))
#     return dup

def generate_all():
    students = generate_students()
    # for student in students:
    #     dup = maybe_duplicate_student(student)
    #     if dup:
    #         students.append(dup)
    return students





def write_students_csv(rows):
    header = [
        "id","student_first_name","student_last_name","date_of_birth", "gender", "grade_level",
        "student_email","student_phone", "contact_address", "guardian_first_name","guardian_last_name",
        "guardian_email","guardian_phone","created","updated"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} students in: {OUTPUT_FILE}")







if __name__ == "__main__":
    students = generate_all()
    write_students_csv(students)

