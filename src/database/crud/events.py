import sqlite3

# CREATE EVENT
def add_event(conn, event_data):
    try:
        with conn:
            cursor = conn.cursor()

            query = """
                INSERT INTO EVENTS (
                    title,
                    event_type,
                    event_date,
                    start_time,
                    end_time,
                    location,
                    department_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, event_data)
            conn.commit()

            print("Event added!")
            return cursor.lastrowid

    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
        return False
    except sqlite3.Error as e:
        print("Error:", e)


# READ EVENTS
def get_events(conn):
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM EVENTS ORDER BY event_date ASC")
            return cursor.fetchall()

    except sqlite3.Error as e:
        print("Error:", e)
        return []


# SEARCH EVENTS
def search_event(conn, search_term="", date_filter=None):
    try:
        with conn:
            cursor = conn.cursor()

            query = "SELECT * FROM EVENTS WHERE 1=1"
            params = []

            if search_term:
                query += " AND (title LIKE ? OR event_type LIKE ? OR location LIKE ?)"
                params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])

            if date_filter:
                query += " AND event_date = ?"
                params.append(date_filter)

            query += " ORDER BY event_date ASC"

            cursor.execute(query, params)
            return cursor.fetchall()

    except sqlite3.Error as e:
        print("Error:", e)
        return []


# UPDATE EVENT
def update_event(conn, event_id, data: dict):
    try:
        with conn:
            cursor = conn.cursor()

            fields = ", ".join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(event_id)

            query = f"""
                UPDATE EVENTS
                SET {fields}
                WHERE id = ?
            """

            cursor.execute(query, values)
            conn.commit()

            print("Event updated!")
            return cursor.rowcount > 0

    except sqlite3.Error as e:
        print("Error:", e)
        return False


# DELETE EVENT
def delete_event(conn, event_id):
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM EVENTS WHERE id = ?", (event_id,))
            conn.commit()

            print("Event deleted!")
            return cursor.rowcount > 0

    except sqlite3.Error as e:
        print("Error:", e)
        return False