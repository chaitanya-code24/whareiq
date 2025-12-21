from src.db import get_db_connection, release_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    print("DB Connection OK:", result)
    cursor.close()
    release_db_connection(conn)

except Exception as e:
    print("DB Connection Failed:", e)
