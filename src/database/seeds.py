from __future__ import annotations

import random
from datetime import date, timedelta

import bcrypt

from database.crud.students import enroll_student, sync_all_students_for_new_subject

SEED_RANDOM = random.Random(20260518)
TARGET_ADMIN_COUNT = 1
TARGET_DEPARTMENT_COUNT = 5
TARGET_COURSE_COUNT = 6
TARGET_STUDENT_COUNT = 30
TARGET_SUBJECT_COUNT = 30
TARGET_EVENT_COUNT = 25
TARGET_ANNOUNCEMENT_COUNT = 25

DEPARTMENTS = [
    ("College of Information Technology",),
    ("College of Business",),
    ("College of Education",),
    ("College of Hospitality Management",),
    ("College of Psychology",),
]

COURSES = [
    ("BS Information Technology", 1),
    ("BS Computer Science", 1),
    ("BS Business Administration", 2),
    ("BS Education", 3),
    ("BS Hospital Management", 4),
    ("BS Psychology", 5),
]

COURSE_ABBREV = {
    1: "IT",
    2: "CS",
    3: "BA",
    4: "ED",
    5: "HM",
    6: "PSY",
}

FIRST_NAMES = [
    "Alyssa", "Ben", "Carla", "Diego", "Ella", "Finn", "Gia", "Hector",
    "Iris", "Jasper", "Kara", "Liam", "Maya", "Noah", "Opal", "Pablo",
    "Quinn", "Rina", "Sean", "Tara", "Uma", "Vince", "Willa", "Xavier",
    "Yna", "Zane",
]

LAST_NAMES = [
    "Bautista", "Cruz", "Delos Santos", "Flores", "Garcia", "Hernandez",
    "Ignacio", "Jimenez", "Luna", "Mendoza", "Navarro", "Ocampo", "Pascual",
    "Quinto", "Reyes", "Santos", "Torres", "Uy", "Valdez", "Yap",
]

STREET_NAMES = [
    "Acacia", "Bamboo", "Cedar", "Dahlia", "Elm", "Fern", "Grove", "Holly",
    "Ivy", "Jade", "Kale", "Larch", "Maple", "Narra", "Olive", "Pine",
]

CITIES = [
    "Quezon City", "Pasig City", "Makati City", "Taguig City", "Manila", "Mandaluyong",
]

EVENT_TITLES = [
    "Student Leadership Summit",
    "Academic Excellence Forum",
    "Campus Innovation Fair",
    "Department Orientation",
    "Research Colloquium",
    "Wellness and Mental Health Talk",
    "Career Pathways Workshop",
    "Community Outreach Day",
    "Sports Fest Tryouts",
    "Code and Coffee Session",
]

ANNOUNCEMENT_TITLES = [
    "Midterm Schedule Advisory",
    "Library Service Update",
    "Enrollment Deadline Reminder",
    "Scholarship Application Open",
    "Campus Wi-Fi Maintenance",
    "Holiday Class Suspension",
    "Faculty Consultation Hours",
    "Student Portal Upgrade",
    "Laboratory Safety Reminder",
    "Upcoming Department Meeting",
]

SUBJECT_TITLES = [
    "Programming Fundamentals",
    "Data Structures",
    "Database Systems",
    "Web Development",
    "Algorithms",
    "Operating Systems",
    "Network Essentials",
    "Research Methods",
    "Technical Writing",
    "Information Security",
    "Systems Analysis",
    "Cloud Fundamentals",
    "Mobile Development",
    "Ethics in Computing",
    "Project Management",
    "Business Communication",
    "Financial Accounting",
    "Human Resource Management",
    "Education Psychology",
    "Classroom Management",
    "Hospitality Operations",
    "Food and Beverage Service",
    "Abnormal Psychology",
    "Child Development",
    "Statistics for Analytics",
    "Software Engineering",
    "Database Administration",
    "Applied Networking",
    "Capstone Planning",
    "Internship Preparation",
]


def _hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _table_count(conn, table_name: str) -> int:
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]


def _dedupe_by_columns(conn, table_name: str, id_column: str, key_columns: list[str]):
    cursor = conn.cursor()
    key_expr = ", ".join(key_columns)
    cursor.execute(
        f"""
        DELETE FROM {table_name}
        WHERE {id_column} NOT IN (
            SELECT MIN({id_column})
            FROM {table_name}
            GROUP BY {key_expr}
        )
        """
    )


def _build_seed_students():
    students = [
        (
            "25-0000",
            "Castillo, Cleven R.",
            1,
            1,
            "demo10@plv.edu.ph",
            "09123456789",
            "789 Oak Lane, Suite 100",
            "Active",
            "2026-05-17",
            _hash_password("demo10@plv.edu.ph"),
        )
    ]

    for index in range(1, TARGET_STUDENT_COUNT):
        student_id = f"25-{index:04d}"
        first_name = SEED_RANDOM.choice(FIRST_NAMES)
        last_name = SEED_RANDOM.choice(LAST_NAMES)
        middle_initial = chr(ord("A") + (index % 26))
        course_id = SEED_RANDOM.randint(1, 6)
        year_level = SEED_RANDOM.randint(1, 4)
        email_address = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}.{index}@plv.edu.ph"
        contact_number = f"09{SEED_RANDOM.randint(100000000, 999999999)}"
        house_number = f"{SEED_RANDOM.randint(1, 999)} {SEED_RANDOM.choice(STREET_NAMES)} St., {SEED_RANDOM.choice(CITIES)}"
        account_status = "Active" if index % 5 else "Inactive"
        enrollment_date = date(2025 + (index % 2), SEED_RANDOM.randint(1, 12), SEED_RANDOM.randint(1, 28)).isoformat()
        students.append(
            (
                student_id,
                f"{last_name}, {first_name} {middle_initial}.",
                course_id,
                year_level,
                email_address,
                contact_number,
                house_number,
                account_status,
                enrollment_date,
                _hash_password(email_address),
            )
        )

    return students


def _build_seed_subjects():
    subjects = []
    subject_index = 1

    # Ensure every course/year pair has at least one subject.
    for course_id, course_name in enumerate([course[0] for course in COURSES], start=1):
        for year_level in range(1, 5):
            title = SUBJECT_TITLES[(subject_index - 1) % len(SUBJECT_TITLES)]
            subject_name = f"{title} ({course_name})"
            subject_code = f"{COURSE_ABBREV.get(course_id, 'GEN')}{year_level}{subject_index:02d}"
            units = float(3 if subject_index % 3 else 2)
            scheduled_day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][subject_index % 5]
            start_hour = 7 + (subject_index % 5)
            end_hour = start_hour + 1
            start_time = f"{start_hour}:00 AM"
            end_time = f"{end_hour}:00 AM"
            subjects.append((subject_name, subject_code, year_level, f"Prof. {subject_index}", course_id, units, scheduled_day, start_time, end_time))
            subject_index += 1

    while len(subjects) < TARGET_SUBJECT_COUNT:
        course_id = SEED_RANDOM.randint(1, 6)
        year_level = SEED_RANDOM.randint(1, 4)
        title = SUBJECT_TITLES[len(subjects) % len(SUBJECT_TITLES)]
        subject_name = f"{title} ({course_id}-{year_level}-{len(subjects) + 1})"
        subject_code = f"{COURSE_ABBREV.get(course_id, 'GEN')}{year_level}{len(subjects) + 1:02d}"
        units = float(SEED_RANDOM.choice([2, 3, 4]))
        scheduled_day = SEED_RANDOM.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        start_hour = SEED_RANDOM.randint(7, 16)
        start_time = f"{start_hour}:00 AM"
        end_time = f"{start_hour + 1}:00 AM"
        subjects.append((subject_name, subject_code, year_level, f"Prof. {len(subjects) + 1}", course_id, units, scheduled_day, start_time, end_time))

    return subjects


def _build_seed_events():
    events = []
    base_date = date(2026, 5, 18)
    for index in range(TARGET_EVENT_COUNT):
        event_title = f"{SEED_RANDOM.choice(EVENT_TITLES)} {index + 1}"
        event_type = SEED_RANDOM.choice(["Academic Sports", "Seminar", "Workshop", "Orientation"])
        event_date = (base_date + timedelta(days=index * 2 + (index % 3))).isoformat()
        start_hour = 8 + (index % 5)
        end_hour = start_hour + 2
        start_time = f"{start_hour}:00 AM"
        end_time = f"{end_hour}:00 AM"
        location = f"Hall {chr(65 + (index % 6))}"
        department_id = SEED_RANDOM.choice([1, 2, 3, 4, 5, None])
        events.append((event_title, event_type, event_date, start_time, end_time, location, department_id))
    return events


def _build_seed_announcements():
    announcements = []
    categories = ["URGENT", "ACADEMICS", "CAMPUS"]
    for index in range(TARGET_ANNOUNCEMENT_COUNT):
        title = f"{SEED_RANDOM.choice(ANNOUNCEMENT_TITLES)} {index + 1}"
        category = categories[index % len(categories)]
        content = (
            f"This is seeded announcement {index + 1}. "
            f"Please review your department updates and upcoming deadlines."
        )
        department_id = SEED_RANDOM.choice([1, 2, 3, 4, 5, None])
        announcements.append((title, category, content, department_id))
    return announcements


def _seed_departments_and_courses(conn):
    cursor = conn.cursor()
    _dedupe_by_columns(conn, "DEPARTMENT", "id", ["department_name"])
    _dedupe_by_columns(conn, "COURSES", "course_id", ["course_name"])

    for department_name, in DEPARTMENTS:
        cursor.execute(
            "SELECT 1 FROM DEPARTMENT WHERE department_name = ? LIMIT 1",
            (department_name,),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO DEPARTMENT (department_name) VALUES (?)",
                (department_name,),
            )

    for course_name, department_id in COURSES:
        cursor.execute(
            "SELECT 1 FROM COURSES WHERE course_name = ? LIMIT 1",
            (course_name,),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO COURSES (course_name, department_id) VALUES (?, ?)",
                (course_name, department_id),
            )


def _seed_admin(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM ADMIN WHERE username = ? LIMIT 1", ("admin",))
    if cursor.fetchone():
        return

    cursor.execute(
        "INSERT OR IGNORE INTO ADMIN (username, password) VALUES (?, ?)",
        ("admin", _hash_password("Admin@Admin123")),
    )


def _seed_students(conn):
    cursor = conn.cursor()
    students = _build_seed_students()
    for student in students:
        cursor.execute(
            """
            INSERT OR IGNORE INTO STUDENTS
            (student_id, full_name, course_id, year_level, email_address, contact_number, house_number, account_status, enrollment_date, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            student,
        )


def _seed_subjects(conn):
    cursor = conn.cursor()
    subjects = _build_seed_subjects()
    for subject in subjects:
        cursor.execute(
            """
            INSERT OR IGNORE INTO SUBJECTS
            (subject_name, subject_code, year_level, teacher, course_id, units, scheduled_day, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            subject,
        )


def _seed_events(conn):
    cursor = conn.cursor()
    existing_count = _table_count(conn, "EVENTS")
    if existing_count >= TARGET_EVENT_COUNT:
        return

    events = _build_seed_events()
    for event in events[existing_count:TARGET_EVENT_COUNT]:
        cursor.execute(
            """
            INSERT INTO EVENTS
            (title, event_type, event_date, start_time, end_time, location, department_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            event,
        )


def _seed_announcements(conn):
    cursor = conn.cursor()
    existing_count = _table_count(conn, "ANNOUNCEMENTS")
    if existing_count >= TARGET_ANNOUNCEMENT_COUNT:
        return

    announcements = _build_seed_announcements()
    for announcement in announcements[existing_count:TARGET_ANNOUNCEMENT_COUNT]:
        cursor.execute(
            """
            INSERT INTO ANNOUNCEMENTS
            (title, category, content, department_id)
            VALUES (?, ?, ?, ?)
            """,
            announcement,
        )


def _seed_enrollments_and_grades(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT subject_id, course_id, year_level FROM SUBJECTS")
    subjects = cursor.fetchall()

    cursor.execute("SELECT student_id, course_id, year_level FROM STUDENTS")
    students = cursor.fetchall()

    for student_id, course_id, year_level in students:
        enroll_student(conn, student_id, course_id, year_level)

    for subject_id, course_id, year_level in subjects:
        sync_all_students_for_new_subject(conn, subject_id)

    cursor.execute("SELECT student_id, subject_id FROM STUDENT_SUBJECTS")
    rows = cursor.fetchall()
    for student_id, subject_id in rows:
        if SEED_RANDOM.random() < 0.65:
            grade = round(SEED_RANDOM.uniform(1.25, 3.75), 2)
            cursor.execute(
                "UPDATE STUDENT_SUBJECTS SET grade = ? WHERE student_id = ? AND subject_id = ?",
                (grade, student_id, subject_id),
            )


def pre_seed_db(conn):
    print("Seeding Started...")
    try:
        _seed_departments_and_courses(conn)
        _seed_admin(conn)
        _seed_subjects(conn)
        _seed_students(conn)
        conn.commit()

        _seed_enrollments_and_grades(conn)
        _seed_events(conn)
        _seed_announcements(conn)
        conn.commit()
    except Exception as e:
        print(f"Seeding error: {e}")
    finally:
        print("Seeding Successfully.")
