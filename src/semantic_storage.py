from db import execute_select, get_db_connection, release_db_connection
from logical_domain_detector import build_logical_domain_map
from measure_auto_mapper import build_measure_map
from dimension_auto_mapper import build_dimension_map
import json


# ---------------------------------
# Store Semantic Mappings
# ---------------------------------

def store_semantic_mappings():
    logical_schema = build_logical_domain_map()
    measure_map = build_measure_map()
    dimension_map = build_dimension_map()

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for table, meta in logical_schema.items():
            table_domain = meta["table_domain"]
            dimensions = dimension_map.get(table, {})
            measures = measure_map.get(table, {})
            technical_fields = meta["technical_fields"]
            ignored_fields = meta["ignored_fields"]

            cursor.execute(
                """
                INSERT INTO semantic_mappings (
                    table_name,
                    table_domain,
                    dimensions,
                    measures,
                    technical_fields,
                    ignored_fields
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (table_name)
                DO UPDATE SET
                    table_domain = EXCLUDED.table_domain,
                    dimensions = EXCLUDED.dimensions,
                    measures = EXCLUDED.measures,
                    technical_fields = EXCLUDED.technical_fields,
                    ignored_fields = EXCLUDED.ignored_fields;
                """,
                (
                    table,
                    table_domain,
                    json.dumps(dimensions),
                    json.dumps(measures),
                    json.dumps(technical_fields),
                    json.dumps(ignored_fields)
                )
            )

        conn.commit()
        cursor.close()

    except Exception as e:
        raise Exception(f"Failed to store semantic mappings: {str(e)}")

    finally:
        if conn is not None:
            release_db_connection(conn)


# ---------------------------------
# Load Semantic Mappings
# ---------------------------------

def load_semantic_mappings():
    rows = execute_select(
    """
    SELECT table_name, table_domain, dimensions, measures,
           technical_fields, ignored_fields
    FROM semantic_mappings
    WHERE table_name != 'semantic_mappings';
    """
)
    mappings = {}

    for row in rows:
        mappings[row[0]] = {
            "table_domain": row[1],
            "dimensions": row[2],
            "measures": row[3],
            "technical_fields": row[4],
            "ignored_fields": row[5]
        }

    return mappings
