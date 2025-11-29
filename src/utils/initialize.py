from initialize_students import generate_all, write_students_csv
from initialize_subjects import generate_subjects, write_subjects_csv
from initialize_tutors import generate_tutors, write_tutors_csv
from initialize_sessions import generate_sessions, write_sessions_csv
from initialize_specialities import generate_specialties, write_specialities_csv

students = generate_all()
write_students_csv(students)

subjects = generate_subjects()
write_subjects_csv(subjects)

tutors = generate_tutors()
write_tutors_csv(tutors)

sessions = generate_sessions()
write_sessions_csv(sessions)

specialties = generate_sessions()
write_sessions_csv(specialties)
