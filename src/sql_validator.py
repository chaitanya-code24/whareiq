import re


# ---------------------------------
# SQL Safety Validator (V1)
# ---------------------------------

FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop", "alter",
    "create", "truncate", "grant", "revoke", "merge"
]

FORBIDDEN_PATTERNS = [
    r";",           # stacked queries
    r"--",          # inline comments
    r"/\*",         # block comment start
    r"\*/"          # block comment end
]


def validate_sql(sql: str) -> bool:
    """
    Validates that a SQL query is safe for read-only execution.

    Rules:
    - Must be a SELECT statement
    - Must not contain forbidden SQL keywords
    - Must not contain stacked queries or comments
    """

    if not sql or not isinstance(sql, str):
        raise ValueError("Empty or invalid SQL")

    normalized = sql.strip().lower()

    # 1. Must start with SELECT
    if not normalized.startswith("select"):
        raise ValueError("Only SELECT statements are allowed")

    # 2. Block forbidden keywords
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{kw}\b", normalized):
            raise ValueError(f"Forbidden SQL keyword detected: {kw}")

    # 3. Block injection patterns
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, sql):
            raise ValueError("Potentially dangerous SQL pattern detected")

    return True
