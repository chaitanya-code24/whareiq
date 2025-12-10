from measure_resolver import resolve_measures
from dimension_resolver import resolve_dimensions
from join_resolver import build_join_plan
from time_filter_resolver import resolve_time_filter


# ---------------------------------
# Full SQL Builder (Production V1)
# ---------------------------------

def build_sql(plan: dict):
    """
    Builds a full deterministic SQL query from a WhareIQ semantic plan.

    Returns:
      {
        "sql": "SELECT ...",
        "select": "...",
        "from": "...",
        "where": "...",
        "group_by": "...",
        "limit": 100
      }
    """

    # 1. Resolve semantic components
    resolved_measures = resolve_measures(plan)
    resolved_dimensions = resolve_dimensions(plan)

    join_plan = build_join_plan(resolved_measures, resolved_dimensions)
    base_table = join_plan["base_table"]

    if base_table is None:
        raise ValueError("No base table could be determined from measures/dimensions")

    time_filter = resolve_time_filter(plan, base_table)

    # 2. Build SELECT clause
    select_parts = []

    for d in resolved_dimensions:
        select_parts.append(d["select_sql"])

    for m in resolved_measures:
        select_parts.append(m["sql"])

    if not select_parts:
        raise ValueError("SQL builder cannot construct SELECT with no dimensions or measures")

    select_clause = "SELECT " + ", ".join(select_parts)

    # 3. FROM / JOIN clause
    from_clause = "FROM " + join_plan["from_sql"]

    # 4. WHERE clause (time filters only for V1)
    where_clauses = []
    where_clauses.extend(time_filter["where_clauses"])

    where_clause = ""
    if where_clauses:
        where_clause = "WHERE " + " AND ".join(where_clauses)

    # 5. GROUP BY (only if measures are present)
    group_by_clause = ""
    if resolved_measures and resolved_dimensions:
        group_cols = [d["group_by_sql"] for d in resolved_dimensions]
        group_by_clause = "GROUP BY " + ", ".join(group_cols)

    # 6. LIMIT
    limit = plan.get("limit", 100)
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("Invalid LIMIT value in semantic plan")

    limit_clause = f"LIMIT {limit}"

    # 7. Final SQL Assembly
    sql_parts = [
        select_clause,
        from_clause,
        where_clause,
        group_by_clause,
        limit_clause
    ]

    # remove empty parts
    final_sql = " ".join([p for p in sql_parts if p])

    return {
        "sql": final_sql,
        "select": select_clause,
        "from": from_clause,
        "where": where_clause,
        "group_by": group_by_clause,
        "limit": limit
    }
