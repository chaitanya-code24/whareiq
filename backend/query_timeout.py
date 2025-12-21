from db import get_db_connection, release_db_connection


# ---------------------------------
# Query Timeout Executor (V1)
# ---------------------------------

def execute_with_timeout(sql: str, timeout_ms: int = 2000):
    """
    Executes a SQL query with a hard PostgreSQL statement timeout.

    - timeout_ms is enforced by the database
    - Query is automatically canceled if it exceeds the limit
    """

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Set timeout for this transaction
        cursor.execute(f"SET statement_timeout = {timeout_ms}")

        cursor.execute(sql)
        rows = cursor.fetchall()

        cursor.close()
        return rows

    finally:
        if conn is not None:
            release_db_connection(conn)

