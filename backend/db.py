import psycopg2
import psycopg2.pool
import os
from dotenv import load_dotenv
from pathlib import Path
from crypto import decrypt
# ---------------------------------
# Load .env from project root
# ---------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

# ---------------------------------
# Postgres Connection Pool
# ---------------------------------
DATABASE_POOL = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

# ---------------------------------
# Internal DB Alias (Semantic Clarity)
# ---------------------------------
def get_internal_db_connection():
    """
    Returns a connection to WhareIQ's internal metadata database.
    """
    return get_db_connection()

# ---------------------------------
# Get / Release DB Connection
# ---------------------------------
def get_db_connection():
    try:
        return DATABASE_POOL.getconn()
    except Exception as e:
        raise Exception(f"Failed to get DB connection: {str(e)}")


def release_db_connection(conn):
    if conn is not None:
        DATABASE_POOL.putconn(conn)


# ---------------------------------
# Read-Only Execution Helper
# ---------------------------------
def execute_select(query: str, params=None):
    """
    Execute a SELECT-only query safely using the connection pool.

    Enforces:
    - Query must start with SELECT (case-insensitive, ignoring leading spaces).
    """

    # Basic read-only enforcement
    stripped = query.lstrip().lower()
    if not stripped.startswith("select"):
        raise ValueError("Only SELECT queries are allowed in WhareIQ V1.")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        raise Exception(f"SELECT query failed: {str(e)}")
    finally:
        if conn is not None:
            release_db_connection(conn)

def get_user_database_credentials(user_id: str):
    conn = get_internal_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT host, port, db_name, username, encrypted_password
        FROM user_database
        WHERE user_id = %s
    """, (user_id,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None

    return {
        "host": row[0],
        "port": row[1],
        "db_name": row[2],
        "username": row[3],
        "password": decrypt(row[4]),
    }
