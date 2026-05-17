import sqlite3

# CREATE ANNOUNCEMENT
def add_announcement(conn, announcement_data):
    try:
        with conn:
            cursor = conn.cursor()

            query = """
                INSERT INTO ANNOUNCEMENTS (
                    title,
                    category,
                    content,
                    department_id
                )
                VALUES (?, ?, ?, ?)
            """

            cursor.execute(query, announcement_data)
            conn.commit()

            print("Announcement added!")

    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
        return False
    except sqlite3.Error as e:
        print("Error:", e)


# READ ANNOUNCEMENTS
def get_announcements(conn):
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ANNOUNCEMENTS ORDER BY created_at DESC")
            return cursor.fetchall()

    except sqlite3.Error as e:
        print("Error:", e)
        return []


# DELETE ANNOUNCEMENT
def delete_announcement(conn, announcement_id):
    try:
        with conn:
            cursor = conn.cursor()

            query = """
                DELETE FROM ANNOUNCEMENTS
                WHERE id = ?
            """

            cursor.execute(query, (announcement_id,))
            conn.commit()

            print("Announcement deleted!")

    except sqlite3.Error as e:
        print("Error:", e)