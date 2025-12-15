import re


# ---------------------------------
# Hard Row Limit Enforcer (V1)
# ---------------------------------

LIMIT_REGEX = re.compile(r"\blimit\s+(\d+)\b", re.IGNORECASE)


def enforce_limit(sql: str, max_limit: int = 1000) -> str:
    """
    Ensures SQL has a LIMIT and that it does not exceed max_limit.

    - If no LIMIT exists → append LIMIT max_limit
    - If LIMIT exists and > max_limit → replace with max_limit
    """

    if not sql or not isinstance(sql, str):
        raise ValueError("Invalid SQL")

    match = LIMIT_REGEX.search(sql)

    # No LIMIT → append one
    if not match:
        return sql.rstrip() + f" LIMIT {max_limit}"

    current_limit = int(match.group(1))

    # LIMIT is acceptable
    if current_limit <= max_limit:
        return sql

    # LIMIT too large → replace
    return LIMIT_REGEX.sub(f"LIMIT {max_limit}", sql)
