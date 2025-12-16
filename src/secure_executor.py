from sql_builder import build_sql
from sql_validator import validate_sql
from allowlist_validator import validate_allowlist
from limit_enforcer import enforce_limit
from query_timeout import execute_with_timeout


# ---------------------------------
# Secure Semantic Query Executor
# ---------------------------------

DEFAULT_MAX_LIMIT = 1000
DEFAULT_TIMEOUT_MS = 2000


def execute_semantic_query(plan: dict):
    """
    Executes a semantic query safely and deterministically.

    Pipeline:
      Semantic Plan
        → SQL Builder
        → SQL Validator
        → Allowlist Validator
        → Hard Limit Enforcer
        → Timeout-enforced Execution

    Returns:
      {
        "sql": final_sql,
        "rows": query_result_rows
      }
    """

    # 1. Build SQL
    sql_info = build_sql(plan)
    raw_sql = sql_info["sql"]

    # 2. Validate SQL syntax & safety
    validate_sql(raw_sql)

    # 3. Enforce semantic allowlist
    validate_allowlist(raw_sql)

    # 4. Enforce hard row limit
    final_sql = enforce_limit(raw_sql, max_limit=DEFAULT_MAX_LIMIT)

    # 5. Execute with timeout
    rows = execute_with_timeout(final_sql, timeout_ms=DEFAULT_TIMEOUT_MS)

    return {
        "sql": final_sql,
        "rows": rows
    }

