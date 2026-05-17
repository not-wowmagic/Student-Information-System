ALLOWED_TABLE_COLUMNS = {
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
    "EVENTS": {
        "id",
        "title",
        "event_type",
        "event_date",
        "start_time",
        "end_time",
        "location",
        "department_id",
    },
    "ANNOUNCEMENTS": {
        "id",
        "department_id",
        "title",
        "category",
        "content",
        "created_at",
    },
    "STUDENT_SUBJECTS": {"id", "student_id", "subject_id", "grade"},
}


def _validate_identifier(table_name: str, column_name: str) -> tuple[str, str]:
    table_norm = table_name.upper()
    column_norm = column_name.lower()

    allowed = ALLOWED_TABLE_COLUMNS.get(table_norm)
    if not allowed or column_norm not in allowed:
        raise ValueError(f"Invalid table/column: {table_name}.{column_name}")

    return table_norm, column_norm


def find_by_column(conn, table_name: str, column_name: str, value: str):
    table_norm, column_norm = _validate_identifier(table_name, column_name)
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT * FROM {table_norm} 
        WHERE {column_norm} = ?
    """, (value,))

    return cursor.fetchone()