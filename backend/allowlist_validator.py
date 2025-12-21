import re
from semantic_storage import load_semantic_mappings


# ---------------------------------
# Allowlist Validator (V1)
# ---------------------------------

TABLE_PATTERN = re.compile(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)
JOIN_PATTERN = re.compile(r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)

COLUMN_PATTERN = re.compile(
    r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b"
)


def extract_tables(sql: str) -> set:
    tables = set()

    for match in TABLE_PATTERN.findall(sql):
        tables.add(match)

    for match in JOIN_PATTERN.findall(sql):
        tables.add(match)

    return tables


def extract_columns(sql: str) -> set:
    """
    Extracts (table, column) pairs like users.email
    """
    return set(COLUMN_PATTERN.findall(sql))


def validate_allowlist(sql: str) -> bool:
    """
    Validates that SQL only touches allowed tables and allowed columns
    based on semantic mappings.

    Technical fields are NOT allowed.
    """

    semantic_mappings = load_semantic_mappings()

    allowed_tables = set(semantic_mappings.keys())

    # ---------------------------------
    # 1. Validate tables
    # ---------------------------------
    used_tables = extract_tables(sql)

    for table in used_tables:
        if table not in allowed_tables:
            raise ValueError(f"Table '{table}' is not allowed by semantic mappings")

    # ---------------------------------
    # 2. Validate columns
    # ---------------------------------
    used_columns = extract_columns(sql)

    for table, column in used_columns:
        if table not in semantic_mappings:
            raise ValueError(f"Table '{table}' is not allowed")

        allowed_dimensions = semantic_mappings[table].get("dimensions", {})
        allowed_measures = semantic_mappings[table].get("measures", {})

        allowed_columns = set(allowed_dimensions.values()) | set(allowed_measures.values())

        if column not in allowed_columns:
            raise ValueError(
                f"Column '{table}.{column}' is not allowed (technical or unknown field)"
            )

    return True
