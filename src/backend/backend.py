from database.crud.announcement import add_announcement
from database.crud.events import add_event
from database.crud.students import add_student, enroll_student, sync_all_students_for_new_subject
from database.crud.subjects import add_subject
from database.db_utils import find_by_column
from src.backend.login_state import load_login_credentials, save_login_credentials
import bcrypt

import sqlite3

def validate_auth(conn, username: str, password: str):
    try:
        with conn:
            cursor = conn.cursor()


            query = "SELECT * FROM ADMIN WHERE username = ?"
            cursor.execute(query, (username,))
            row = cursor.fetchone()

            if row is not None:
                if password == row[2]:
                    return [row[0], "admin"]

            query = "SELECT * FROM STUDENTS WHERE student_id = ?"
            cursor.execute(query, (username,))
            row = cursor.fetchone()

            print("ROW:", row)
            if row is not None:
                stored_hash = row[9]
                print("CHECKING PASSWORD:", password)
                print("AGAINST HASH:", stored_hash)
                if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
                    return [row[0], "student"]

            return None

    except sqlite3.Error as e:
        print("Error:", e)



def create_new_students(conn, student_data: list, mock=False):
    # student_id,
    # full_name,
    # course_id,
    # year_level,
    # email_address,
    # contact_number,
    # house_number,
    # account_status,
    # enrollment_date,
    # password

    student_id = student_data[0]
    full_name: str = student_data[1]
    course_text = student_data[2]
    year_level = student_data[3]
    email_address = student_data[4]
    contact_number = student_data[5]
    house_number = student_data[6]
    account_status = student_data[7]
    enrollment_date = student_data[8]


    if not student_id:
        print("no student id!")
        return

    if not full_name:
        print("no student full_name!")
        return


    if not course_text:
        print("no student course_text!")
        return


    if not mock:
        course_data = find_by_column(conn, "COURSES", "course_name", course_text)

        print(course_data)
        if not course_data:
            print("no course data found")

        course_text = course_data[0]


    if not year_level:
        print("no student year_level!")
        return False, "No student year level"

    if not email_address:
        print("no student email_address!")
        return False, "No student email_address!"


    if not account_status:
        print("no student account_status!")
        return  False, "No  student account_status!"

    if not enrollment_date:
        print("no student enrollment_date!")
        return False, "No student enrollment_date!"


    first_name = full_name.split(", ")

    if len(first_name) < 2:
        print("Name format must be 'Lastname, Firstname'")
        return False, "Name format must be 'Lastname, Firstname'"

    real_password = email_address

    student_data = [
        student_id,
        full_name,
        course_text,
        year_level,
        email_address,
        contact_number,
        house_number,
        account_status,
        enrollment_date,
        bcrypt.hashpw(real_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    ]

    # create a students
    data  =  add_student(conn, student_data)
    is_success = data[0]
    err_message = data[1]
    enroll_student(conn, student_id, course_text, year_level)

    return is_success, err_message

# def sync_all_students_for_new_subject(conn, subject_id):
def create_new_subject(conn, subject_data: list):
    # subject_data:
    # [0] subject_code
    # [1] subject_name
    # [2] year level
    # [3] teacher
    # [4] course_name  (will be converted to course_id)
    # [5] units
    # [6] scheduled_day
    # [7] start_time
    # [8] end_time

    subject_code   = subject_data[0]
    subject_name   = subject_data[1]
    year_level     = subject_data[2]
    teacher        = subject_data[3]
    course_text    = subject_data[4]
    units          = subject_data[5]
    scheduled_day  = subject_data[6]
    start_time     = subject_data[7]
    end_time       = subject_data[8]

    if not subject_code:
        return False, "No subject code!"

    if not subject_name:
        return False, "No subject name!"

    if not teacher:
        return False, "No teacher!"

    if not course_text:
        return False, "No department!"

    if not units:
        return False, "No units!"

    if not scheduled_day:
        return False, "No scheduled day!"

    if not start_time:
        return False, "No start time!"

    if not end_time:
        return False, "No end time!"

    # convert course_name → course_id
    course_data = find_by_column(conn, "COURSES", "course_name", course_text)

    if not course_data:
        return (False, "No course data found!")

    course_id = course_data[0]

    subject_data = [
        subject_name,
        subject_code,
        year_level,
        teacher,
        course_id,
        float(units),
        scheduled_day,
        start_time,
        end_time
    ]

    data = add_subject(conn, subject_data)
    is_success = data[0]
    err_message = data[1]
    subject_data = find_by_column(conn, "SUBJECTS", "subject_name", subject_name)
    sync_all_students_for_new_subject(conn, subject_data[0])

    return is_success, err_message

def create_new_event(conn, event_data: list):
    # event_data:
    # [0] title
    # [1] event_type
    # [2] event_date
    # [3] start_time
    # [4] end_time
    # [5] location
    # [6] department

    title       = event_data[0]
    event_type  = event_data[1]
    event_date  = event_data[2]
    start_time  = event_data[3]
    end_time    = event_data[4]
    location    = event_data[5]
    department  = event_data[6]

    if not title:
        print("no title!")
        return

    if not event_type:
        print("no event type!")
        return

    if not event_date:
        print("no event date!")
        return

    if not department:
        print("no department!")
        return

    # convert course_name → course_id
    department_data = find_by_column(conn, "DEPARTMENT", "department_name", department)

    print(department_data)
    if not department_data:
        print("no department data found!")
        return


    event_data[6] = department_data[0]

    print(event_data)
    add_event(conn, event_data)

def create_new_announcement(conn, announcement_data: list):
    title      = announcement_data[0]
    category   = announcement_data[1]
    content    = announcement_data[2]
    department = announcement_data[3]  # "All Departments" or department name
    print(f"Looking for department: {department}")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM DEPARTMENT")
    print(f"All departments in DB: {cursor.fetchall()}")  # ← what's actually stored?


    if not title:
        print("no title!")
        return

    if not content:
        print("no content!")
        return

    # Convert department name → course_id
    if department is None or department == "All Departments":
        course_id = None
    else:
        course_data = find_by_column(conn, "COURSES", "course_name", department)
        course_id = course_data[0] if course_data else None

    add_announcement(conn, [title, category, content, course_id])

# ---- REMEMBER ME -----
def get_credentials(fields):
    data = load_login_credentials()
    if not data:
        return None

    return data.get(fields)

def save_credentials_state(username: str, password: str):
    print("Saving data...")
    save_login_credentials(username, password)
    print("Saving completed...")


