from db import get_db_connection, release_db_connection


# ---------------------------------
# Load Full Physical Schema
# ---------------------------------
def load_physical_schema():
    """
    Introspects PostgreSQL and returns a full physical schema map.

    Output format:
    {
        "table_name": {
            "columns": { "col": "datatype" },
            "primary_key": ["id"],
            "foreign_keys": {
                "col": {
                    "references_table": "other_table",
                    "references_column": "id"
                }
            }
        }
    }
    """

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # -----------------------------
        # 1. Fetch Tables
        # -----------------------------
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = [row[0] for row in cursor.fetchall()]

        schema = {}

        for table in tables:
            schema[table] = {
                "columns": {},
                "primary_key": [],
                "foreign_keys": {}
            }

        # -----------------------------
        # 2. Fetch Columns
        # -----------------------------
        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public';
        """)
        for table, column, dtype in cursor.fetchall():
            if table in schema:
                schema[table]["columns"][column] = dtype

        # -----------------------------
        # 3. Fetch Primary Keys
        # -----------------------------
        cursor.execute("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = 'public';
        """)
        for table, column in cursor.fetchall():
            if table in schema:
                schema[table]["primary_key"].append(column)

        # -----------------------------
        # 4. Fetch Foreign Keys
        # -----------------------------
        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public';
        """)
        for table, column, ref_table, ref_column in cursor.fetchall():
            if table in schema:
                schema[table]["foreign_keys"][column] = {
                    "references_table": ref_table,
                    "references_column": ref_column
                }

        cursor.close()
        return schema

    except Exception as e:
        raise Exception(f"Schema introspection failed: {str(e)}")

    finally:
        if conn is not None:
            release_db_connection(conn)
