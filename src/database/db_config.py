import sqlite3
import os
from database.seeds import pre_seed_db


EXPECTED_TABLE_COLUMNS = {
    "ADMIN": {"admin_id", "username", "password"},
    "DEPARTMENT": {"id", "department_name"},
    "COURSES": {"course_id", "course_name", "department_id"},
    "STUDENTS": {
        "student_id",
        "full_name",
        "course_id",
        "year_level",
        "email_address",
        "contact_number",
        "house_number",
        "account_status",
        "enrollment_date",
        "password",
    },
    "SUBJECTS": {
        "subject_id",
        "subject_name",
        "subject_code",
        "year_level",
        "teacher",
        "course_id",
        "units",
        "scheduled_day",
        "start_time",
        "end_time",
    },
}

def find_db_filepath(path_name: str) -> str:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_FILE_PATH = os.path.join(CURRENT_DIR, "..", "database", path_name)
    return DATABASE_FILE_PATH

def connect_db():
    db_file_path = find_db_filepath("StudentInformationDB.db")

    if not db_file_path:
        print("No database found, creating new one...")

    conn = sqlite3.connect(db_file_path)
    conn.execute("PRAGMA foreign_keys = ON")

    if needs_schema_reset(conn):
        reset_database(conn)

    create_tables(conn)
    pre_seed_db(conn)

    print("[DATABASE CONNECTION]: ESTABLISHED!")
    return conn


def needs_schema_reset(conn):
    cursor = conn.cursor()

    for table_name, expected_columns in EXPECTED_TABLE_COLUMNS.items():
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {row[1] for row in cursor.fetchall()}

        if existing_columns and existing_columns != expected_columns:
            return True

    return False


def reset_database(conn):
    cursor = conn.cursor()

    for table_name in [
        "STUDENT_SUBJECTS",
        "ANNOUNCEMENTS",
        "EVENTS",
        "SUBJECTS",
        "STUDENTS",
        "COURSES",
        "DEPARTMENT",
        "ADMIN",
    ]:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.commit()

def create_tables(conn):
    cursor = conn.cursor()

    # ===== ADMIN TABLE =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ADMIN(
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # ==== COURSES TABLE ====
    cursor.execute("""
           CREATE TABLE IF NOT EXISTS DEPARTMENT(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               department_name TEXT NOT NULL
           )
       """)


    # ==== COURSES TABLE ====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS COURSES(
            course_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name     TEXT NOT NULL,
            department_id   INTEGER NOT NULL,
            
            FOREIGN KEY (department_id) REFERENCES DEPARTMENT(id) ON DELETE CASCADE
        )
    """)


    # ==== STUDENTS TABLE ====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS STUDENTS(
            student_id      TEXT    PRIMARY KEY NOT NULL UNIQUE,
            full_name       TEXT    NOT NULL,
            course_id       INTEGER NOT NULL,
            year_level      INTEGER NOT NULL,
            email_address   TEXT    NOT NULL,
            contact_number  TEXT,
            house_number    TEXT,
            account_status  TEXT    NOT NULL,
            enrollment_date TEXT    NOT NULL,
            password        TEXT    NOT NULL,

            FOREIGN KEY (course_id) REFERENCES COURSES(course_id)
        )
    """)

    # ==== SUBJECTS TABLE ====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SUBJECTS(
            subject_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name  TEXT    NOT NULL UNIQUE,
            subject_code  TEXT    NOT NULL UNIQUE,
            year_level    INTEGER NOT NULL,
            teacher       TEXT    NOT NULL,
            course_id     INTEGER NOT NULL,
            units         REAL    NOT NULL,
            scheduled_day TEXT    NOT NULL,
            start_time    TEXT    NOT NULL,
            end_time      TEXT    NOT NULL,

            FOREIGN KEY (course_id) REFERENCES COURSES(course_id) ON DELETE CASCADE
        )
    """)

    # ==== EVENTS TABLE ====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS EVENTS(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            event_type  TEXT    NOT NULL,
            event_date  TEXT    NOT NULL,
            start_time  TEXT,
            end_time    TEXT,
            location    TEXT,
            department_id INTEGER,
            
            
            FOREIGN KEY (department_id) REFERENCES DEPARTMENT(id)
        )
    """)

    # ==== ANNOUNCEMENTS TABLE ====
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS ANNOUNCEMENTS(
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            department_id  INTEGER,
            title      TEXT    NOT NULL,
            category   TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (department_id) REFERENCES DEPARTMENT(id)
    )
    """)

    # ==== STUDENT_SUBJECTS TABLE ====
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS STUDENT_SUBJECTS(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        grade REAL,
    
        FOREIGN KEY (student_id) REFERENCES STUDENTS(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES SUBJECTS(subject_id) ON DELETE CASCADE ON UPDATE CASCADE,
    
        UNIQUE(student_id, subject_id)
    
    )
    """)

    conn.commit()