import csv
import random
from datetime import datetime, date, timedelta
from pathlib import Path
from initialize_students import rand_business_time
from initialize_sessions import load_csv


OUTPUT_DIR = Path("./data/gold")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "specialties.csv"


sessions = load_csv("data/gold/sessions.csv")



def generate_specialties(): 
    specialties = []
    seen = set()
    for sesh in sessions:
        key = (sesh["tutor_id"], sesh["subject_id"])
        if key not in seen:
            specialties.append({
                "tutor_id": key[0],
                "subject_id": key[1]
            })
            seen.add(key)
    return specialties

def write_specialities_csv(rows):
    header = [
        "tutor_id","subject_id"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} specialities in: {OUTPUT_FILE}")

specialties = generate_specialties()

if __name__ == "__main__":
     write_specialities_csv(specialties)
















