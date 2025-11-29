from initialize_students import rand_created, rand_last_name, rand_first_name, rand_phone, rand_email, rand_address, NUM_STUDENTS, STREET_SUFFIXES, STREETS, ZIP_CODES_NASSAU, ZIP_CODES_SUFFOLK
import csv
from pathlib import Path
from datetime import date, timedelta, datetime
import random

def load_csv(filepath):
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


subjects = load_csv("data/gold/subjects.csv")

NUM_TUTORS = int(NUM_STUDENTS/30)

OUTPUT_DIR = Path("./data/gold")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE_TUTORS = OUTPUT_DIR / "tutors.csv"

def generate_tutors(num_tutors=NUM_TUTORS):
    rows = []

    for tutor_id in range(1, NUM_STUDENTS + 1):

        created = rand_created(tutor_id,2016,10)
        updated = created
        sex = random.choices(population = ['M','F','X'], weights = [0.45,0.54,0.01], k=1)[0]
        id = tutor_id
        first_name = rand_first_name('S',sex)
        last_name = rand_last_name(sex)
        phone = rand_phone('G')
        email = rand_email('G',first_name,last_name)
        hourly_rate = random.choice([40,45,50])
        employment_type = 'Contract'
        address = rand_address()

        rows.append({
            "id": id,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "contact_address_id": address,
            "employment_type": employment_type,
            "hourly_rate": hourly_rate,
            "created": created,
            "updated": updated
        })
    rows = random.sample(rows,NUM_TUTORS)
    return rows

tutors = generate_tutors()

tutors.append({
   "id": 0,
    "first_name": "Stephan",
    "last_name": "Pichardo",
    "phone": "418-861-1574",
    "email": "stephan.pichardo768@somedomain.com",
    "contact_address_id": "498 Spruce Street, 11742",
    "employment_type": "Full-Time",
    "hourly_rate": 0,
    "created": datetime(2016, 1, 1, 0, 0, 0),
    "updated": datetime(2016, 1, 1, 0, 0, 0)
})

def write_tutors_csv(tutors):
    header = [
         "id","first_name","last_name","phone","email","contact_address_id","employment_type","hourly_rate","created","updated"
    ]

    with open(OUTPUT_FILE_TUTORS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(tutors)

    print(f"Generated {len(tutors)} tutors in: {OUTPUT_FILE_TUTORS}")


if __name__ == "__main__":
    tutors = generate_tutors()
    write_tutors_csv(tutors)
