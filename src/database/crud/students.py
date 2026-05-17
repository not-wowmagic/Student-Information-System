import sqlite3
from typing import Any


#student_id TEXT PRIMARY KEY NOT NULL,
#full_name TEXT NOT NULL,
#course_id INTEGER NOT NULL,
#year_level INTEGER NOT NULL,
#email_address TEXT NOT NULL,
#contact_Number INTEGER NOT NULL,
#house_number TEXT NOT NULL,
#account_status TEXT NOT NULL,
#enrollment_date TEXT, NOT NULL
#password TEXT NOT NULL,
def update_student_grade(conn, student_id, subject_id, grade):

    """
    Update a single grade row in STUDENT_SUBJECTS.
    Call once per subject when saving from the grade form.
    """


    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE STUDENT_SUBJECTS
            SET grade = ?
            WHERE student_id = ? AND subject_id = ?
        """, (grade, student_id, subject_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saving grade (student={student_id}, subject={subject_id}):", e)
        return False


def get_student_gwa(conn, student_id):
    """
    Compute the weighted GWA for a student directly from the DB.
    Returns a float rounded to 2 decimal places, or None if no grades yet.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                SUM(SS.grade * SU.units),
                SUM(SU.units)
            FROM STUDENT_SUBJECTS SS
            JOIN SUBJECTS SU ON SS.subject_id = SU.subject_id
            WHERE SS.student_id = ?
              AND SS.grade IS NOT NULL
        """, (student_id,))
        row = cursor.fetchone()
        if row and row[1] and row[1] > 0:
            return round(row[0] / row[1], 2)
        return None
    except sqlite3.Error as e:
        print("Error computing GWA:", e)
        return None


def sync_all_students_for_new_subject(conn, subject_id):
    cursor = conn.cursor()

    # get subject info
    cursor.execute("""
        SELECT course_id, year_level
        FROM SUBJECTS
        WHERE subject_id = ?
    """, (subject_id,))
    subject = cursor.fetchone()

    if not subject:
        return

    course_id, year_level = subject

    # get all students in same course/year
    cursor.execute("""
        SELECT student_id
        FROM STUDENTS
        WHERE course_id = ? AND year_level = ?
    """, (course_id, year_level))

    students = cursor.fetchall()

    # enroll subject to all students
    for (student_id,) in students:
        cursor.execute("""
            INSERT OR IGNORE INTO STUDENT_SUBJECTS
            (student_id, subject_id, grade)
            VALUES (?, ?, NULL)
        """, (student_id, subject_id))

    conn.commit()



def enroll_student(conn, student_id, course_id, year_level):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject_id FROM SUBJECTS
        WHERE course_id = ? AND year_level = ?
    """, (course_id, year_level))
    subjects = cursor.fetchall()

    for subj in subjects:
        cursor.execute("""
            INSERT OR IGNORE INTO STUDENT_SUBJECTS (student_id, subject_id, grade)
            VALUES (?, ?, NULL)
        """, (student_id, subj[0]))

    conn.commit()

def get_student_subjects(conn, student_id):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                STUDENT_SUBJECTS.id,
                STUDENT_SUBJECTS.student_id,
                STUDENT_SUBJECTS.subject_id,
                STUDENT_SUBJECTS.grade,
                SUBJECTS.subject_name,
                SUBJECTS.subject_code,
                SUBJECTS.teacher,
                SUBJECTS.units,
                SUBJECTS.scheduled_day,
                SUBJECTS.start_time,
                SUBJECTS.end_time,
                SUBJECTS.year_level
            FROM STUDENT_SUBJECTS
            JOIN SUBJECTS ON STUDENT_SUBJECTS.subject_id = SUBJECTS.subject_id
            WHERE STUDENT_SUBJECTS.student_id = ?
        """, (student_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error:", e)
        return []


# CREATE
def add_student(conn, student_data):
    try:
        with conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO STUDENTS
                (student_id,
                full_name,
                course_id,
                year_level,
                email_address,
                contact_number,
                house_number,
                account_status,
                enrollment_date,
                password
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, student_data)
            conn.commit()

            return True, "Sucessfully logged in"
    except sqlite3.IntegrityError:
        # Specifically catch duplicate IDs
        print(f"Error: Student ID '{student_data[0]}' already exists!")
        return (False, f"'{student_data[0]}' already exists!")
    except sqlite3.SQLITE_CONSTRAINT_UNIQUE as e:
        print(f"Error: Student ID '{student_data[0]}' already exists!")
        return (False, f"SUBJECT ID '{student_data[0]}' have the code by someone!")
    except sqlite3.Error as e:
        print("Error:", e)
        return (False, "Something error has occured, please contact the dev.")

def get_students(conn):
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM STUDENTS")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print("Error:", e)
        return []


def search_student(conn, student_id):
    try:
        with conn:
            cursor = conn.cursor()

            if student_id:
                query = "SELECT * FROM STUDENTS WHERE student_id = ?"
                cursor.execute(query, (student_id,))
                return cursor.fetchone()
            else:
                query = "SELECT * FROM STUDENTS"
                cursor.execute(query)
                return cursor.fetchall()

                return result
    except sqlite3.Error as e:
        print("Error:", e)


def update_student(conn, student_id, data: dict):
    try:
        with conn:
            cursor = conn.cursor()

            course_or_year_changed = "course_id" in data or "year_level" in data

            if course_or_year_changed:
                # Fetch current values first
                cursor.execute("""
                    SELECT course_id, year_level FROM STUDENTS
                    WHERE student_id = ?
                """, (student_id,))
                current = cursor.fetchone()
                current_course_id  = current[0]
                current_year_level = current[1]

                # Use new values if provided, else keep current
                new_course_id  = data.get("course_id",  current_course_id)
                new_year_level = data.get("year_level", current_year_level)

            # ── Apply the student field updates ──────────────────────────────
            fields = ", ".join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(student_id)

            cursor.execute(f"""
                UPDATE STUDENTS
                SET {fields}
                WHERE student_id = ?
            """, values)

            if course_or_year_changed:
                actually_changed = (
                    new_course_id  != current_course_id or
                    new_year_level != current_year_level
                )

                if actually_changed:
                    # 1. Remove all old subject enrollments
                    cursor.execute("""
                        DELETE FROM STUDENT_SUBJECTS
                        WHERE student_id = ?
                    """, (student_id,))

                    # 2. Get all subjects for new course + year
                    cursor.execute("""
                        SELECT subject_id FROM SUBJECTS
                        WHERE course_id = ? AND year_level = ?
                    """, (new_course_id, new_year_level))
                    subjects = cursor.fetchall()

                    # 3. Enroll student in the new subjects
                    for (subject_id,) in subjects:
                        cursor.execute("""
                            INSERT OR IGNORE INTO STUDENT_SUBJECTS
                            (student_id, subject_id, grade)
                            VALUES (?, ?, NULL)
                        """, (student_id, subject_id))

            conn.commit()

    except sqlite3.Error as e:
        print("Error:", e)

def delete_student(conn, student_id):
    try:
        with conn:
            cursor = conn.cursor()

            query = """
                DELETE FROM STUDENTS
                WHERE student_id = ?
            """
            cursor.execute(query, (student_id,))
            conn.commit()
    except sqlite3.Error as e:
        print("Error:", e)


# ── REPORT QUERY FUNCTIONS ────────────────────────────────────────────────────
def get_student_count(conn):
    """Get total number of students"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM STUDENTS")
        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print("Error getting student count:", e)
        return 0


def get_active_students_count(conn):
    """Get number of active students"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM STUDENTS WHERE account_status = 'Active'")
        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print("Error getting active students count:", e)
        return 0


def get_inactive_students_count(conn):
    """Get number of inactive students"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM STUDENTS WHERE account_status = 'Inactive'")
        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print("Error getting inactive students count:", e)
        return 0


def get_recent_enrollments(conn, limit=10):
    """Get most recently enrolled students"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                STUDENTS.enrollment_date,
                STUDENTS.student_id,
                STUDENTS.full_name,
                COURSES.course_name
            FROM STUDENTS
            JOIN COURSES ON STUDENTS.course_id = COURSES.course_id
            ORDER BY STUDENTS.enrollment_date DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print("Error getting recent enrollments:", e)
        return []


def get_enrollment_by_course(conn):
    """Get enrollment count by course"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COURSES.course_name,
                COUNT(STUDENTS.student_id) as enrollment_count
            FROM COURSES
            LEFT JOIN STUDENTS ON COURSES.course_id = STUDENTS.course_id
            GROUP BY COURSES.course_id, COURSES.course_name
            ORDER BY enrollment_count DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print("Error getting enrollment by course:", e)
        return []


def get_enrollment_by_department(conn):
    """Get enrollment count by department"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                DEPARTMENT.department_name,
                COUNT(DISTINCT STUDENTS.student_id) as enrollment_count
            FROM DEPARTMENT
            LEFT JOIN COURSES ON DEPARTMENT.id = COURSES.department_id
            LEFT JOIN STUDENTS ON COURSES.course_id = STUDENTS.course_id
            GROUP BY DEPARTMENT.id, DEPARTMENT.department_name
            ORDER BY enrollment_count DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print("Error getting enrollment by department:", e)
        return []


def get_subject_enrollment_stats(conn):
    """Get subject enrollment counts and average grades"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                SUBJECTS.subject_code,
                SUBJECTS.subject_name,
                COUNT(STUDENT_SUBJECTS.student_id) as enrollment_count,
                ROUND(AVG(STUDENT_SUBJECTS.grade), 2) as avg_grade
            FROM SUBJECTS
            LEFT JOIN STUDENT_SUBJECTS ON SUBJECTS.subject_id = STUDENT_SUBJECTS.subject_id
            GROUP BY SUBJECTS.subject_id, SUBJECTS.subject_code, SUBJECTS.subject_name
            ORDER BY enrollment_count DESC
            LIMIT 10
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print("Error getting subject enrollment stats:", e)
        return []