import sqlite3

# CREATE SUBJECT
def add_subject(conn, subject_data):
    try:
        with conn:
            cursor = conn.cursor()

            query = """
                INSERT INTO SUBJECTS (
                    subject_name,
                    subject_code,
                    year_level,
                    teacher,
                    course_id,
                    units,
                    scheduled_day,
                    start_time,
                    end_time
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, subject_data)
            conn.commit()

        return (True, "Success!")

    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
        return (False, "Duplicate Key")
    except sqlite3.SQLITE_CONSTRAINT_UNIQUE as e:
        print("Error:", e)
        return (False, "You cannot make a subject, the subject code or subject name is unique")
    except sqlite3.Error as e:
        print("Error:", e)
        return (False, "something error has occured, Please contact the dev")


# READ SUBJECTS
def get_subjects(conn):
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM SUBJECTS")
            return cursor.fetchall()

    except sqlite3.Error as e:
        print("Error:", e)


# UPDATE SUBJECT
def update_subject(conn, subject_id, data: dict):
    try:
        with conn:
            cursor = conn.cursor()

            fields = ", ".join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(subject_id)

            query = f"""
                UPDATE SUBJECTS
                SET {fields}
                WHERE subject_id = ?
            """

            cursor.execute(query, values)
            conn.commit()

            print("Subject updated!")

    except sqlite3.Error as e:
        print("Error:", e)


# DELETE SUBJECT
def delete_subject(conn, subject_id):
    try:
        with conn:
            cursor = conn.cursor()

            query = """
                DELETE FROM SUBJECTS
                WHERE subject_id = ?
            """

            cursor.execute(query, (subject_id,))
            conn.commit()

            print("Subject deleted!")

    except sqlite3.Error as e:
        print("Error:", e)