import csv
from pathlib import Path

OUTPUT_DIR = Path("./data/gold")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "subjects.csv"

subjects = ['Algebra I','Algebra II','Geometry','Precalculus','Calculus','Math','Chemistry','Physics',
            'Social Studies','Language Arts','Foreign Language','Science']

modifiers = ['AP','IB','Regents','SAT','ACT','Grade']

def classify_subject(subject_name):
    if subject_name in ['Chemistry', 'Physics', 'Science']:
        return "Science"
    elif subject_name in ['Algebra I', 'Algebra II', 'Geometry',
                          'Precalculus', 'Calculus', 'Math']:
        return "Math"
    else:
        return "Humanities"
    
def classify_category(category_name):
    if category_name in ['Science','Math']:
        return "STEM"
    else:
        return "Humanities"

def generate_subjects():
    rows_0 = []
    pk = 1
    for subject_name in subjects:
        for modifier in modifiers:
            rows_0.append({
                "id": pk,
                "name": subject_name,
                "modifier": modifier,
                "category1": classify_subject(subject_name),
                "category2":  classify_category(classify_subject(subject_name))
            })
            pk += 1
    keepers = {3,9,15,6,12,18,24,25,30,32,34,35,36,37,38,39,
               42,43,44,45,48,49,51,54,55,56,57,58,59,60,61,
               66,69,72,71}
    rows = [row for row in rows_0 if row["id"] in keepers]
    return rows


def write_subjects_csv(rows):
    header = [
        "id","name","modifier","category1","category2"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} subjects in: {OUTPUT_FILE}")


if __name__ == "__main__":
    subjects = generate_subjects()
    write_subjects_csv(subjects)

