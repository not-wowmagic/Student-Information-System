def find_by_column(conn, table_name: str, column_name: str, value: str):
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT * FROM {table_name} 
        WHERE {column_name} = ?
    """, (value,))

    return cursor.fetchone()