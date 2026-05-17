from backend.backend import create_new_students
from database.crud.students import enroll_student, sync_all_students_for_new_subject

departments = [
    ("College of Information Technology",),
    ("College of Business",),
    ("College of Education",),
    ("College of Hospitality Management",),
    ("College of Psychology",),
]

courses = [
    ("BS Information Technology", 1),
    ("BS Computer Science",       1),
    ("BS Business Administration", 2),
    ("BS Education",              3),
    ("BS Hospital Management",    4),
    ("BS Psychology",             5),
]

admin = [('admin', 'Admin@Admin123')]

student = (
    '25-0000',
    "Castillo, Cleven, R.",
    1,        # course_id
    1,        # year_level
    "demo10@plv.edu.ph",
    "09123456789",
    "789 Oak Lane, Suite 100",
    "Active",
    "2026-05-17",
)

# subject_name, subject_code, teacher, course_id, year_level, units, scheduled_day, start_time, end_time
subjects = [
    ('Introduction to Intermediate Programming', 'CC3', 'John Christian Lorr', 1, 1, 3, "Monday", "7:00 AM", "12:00 PM")
    #                                                                              ↑ year_level added
]

def is_already_seeded(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM COURSES")
    count = cursor.fetchone()[0]
    return count > 0

def pre_seed_db(conn):
    if is_already_seeded(conn):
        print("Already seeded, skipping...")
        return

    print("Seeding Started...")
    try:
        cursor = conn.cursor()

        # 1. Seed departments first
        cursor.executemany("""
            INSERT OR IGNORE INTO DEPARTMENT (department_name)
            VALUES (?)
        """, departments)

        # 2. Seed courses
        cursor.executemany("""
            INSERT OR IGNORE INTO COURSES (course_name, department_id)
            VALUES (?, ?)
        """, courses)

        # 3. Seed admin
        cursor.executemany("""
            INSERT OR IGNORE INTO ADMIN (username, password)
            VALUES (?, ?)
        """, admin)

        # 4. Seed subjects (with year_level)
        cursor.executemany("""
            INSERT OR IGNORE INTO SUBJECTS (
                subject_name, subject_code, teacher,
                course_id, year_level, units,
                scheduled_day, start_time, end_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, subjects)

        conn.commit()

        # 5. Seed student (uses create_new_students which handles bcrypt)
        create_new_students(conn, student, mock=True)

        # 6. Enroll seeded student in matching subjects
        enroll_student(conn, student[0], student[2], student[3])

        # 7. Sync any existing students for new subjects
        cursor.execute("SELECT subject_id FROM SUBJECTS")
        all_subjects = cursor.fetchall()
        for subj in all_subjects:
            sync_all_students_for_new_subject(conn, subj[0])

        conn.commit()

    except Exception as e:
        print(f"Seeding error: {e}")
    finally:
        print("Seeding Successfully.")