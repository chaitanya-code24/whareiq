from schema_reader import load_physical_schema


# ---------------------------------
# Time Column Detection (Multi-candidate, prioritized)
# ---------------------------------

TIME_COLUMN_PRIORITY = [
    "created_at",
    "event_time",
    "order_date",
    "date",
    "timestamp",
    "updated_at"
]

TIME_DATA_TYPES = [
    "timestamp without time zone",
    "timestamp with time zone",
    "date"
]


def find_time_column(base_table: str):
    """
    Detect a canonical time column for the base table, even if there are multiple
    possible time-related columns. Uses a priority-based, deterministic strategy.

    Strategy:
      1. Find all columns whose name contains any of TIME_COLUMN_PRIORITY (in order).
      2. If multiple match, pick the one with the highest priority (lowest index).
      3. If none match by name, look at data types and pick the first time-like dtype.
      4. If still nothing, return None.
    """

    schema = load_physical_schema()

    if base_table not in schema:
        raise ValueError(f"Base table '{base_table}' not found in physical schema")

    columns = schema[base_table]["columns"]

    # 1. Name-based candidates with priority scoring
    candidates = []

    for col_name in columns.keys():
        lower = col_name.lower()
        for idx, pattern in enumerate(TIME_COLUMN_PRIORITY):
            if pattern in lower:
                # lower idx = higher priority
                candidates.append((idx, col_name))
                break  # don't match multiple patterns for same column

    if candidates:
        # sort by priority index, return the best column
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    # 2. Type-based fallback if no name-based match
    for col_name, dtype in columns.items():
        if dtype in TIME_DATA_TYPES:
            return col_name

    # 3. No suitable time column found
    return None


# ---------------------------------
# Time Range → SQL Resolver
# ---------------------------------

def resolve_time_filter(plan: dict, base_table: str):
    """
    Resolves plan['time_range'] into SQL WHERE clauses based on a selected
    canonical time column for the base_table.

    Returns:
      {
        "time_column": "table.col",
        "where_clauses": ["table.col >= ...", "table.col < ..."]
      }

    Or, if no time_range is present:
      {
        "time_column": None,
        "where_clauses": []
      }
    """

    time_range = plan.get("time_range")

    # No time filter requested
    if not time_range:
        return {
            "time_column": None,
            "where_clauses": []
        }

    time_col = find_time_column(base_table)

    if time_col is None:
        raise ValueError(
            f"Time range specified, but no suitable time column found on table '{base_table}'."
        )

    full_col = f"{base_table}.{time_col}"
    clauses = []

    range_type = time_range.get("type")

    # --- Relative days: last_n_days ---
    if range_type == "relative_days":
        n = time_range.get("last_n_days")
        if not isinstance(n, int):
            raise ValueError("relative_days requires integer last_n_days")
        clauses.append(f"{full_col} >= CURRENT_DATE - INTERVAL '{n} days'")

    # --- Relative months: last_n_months ---
    elif range_type == "relative_months":
        n = time_range.get("last_n_months")
        if not isinstance(n, int):
            raise ValueError("relative_months requires integer last_n_months")
        clauses.append(f"{full_col} >= CURRENT_DATE - INTERVAL '{n} months'")

    # --- This month ---
    elif range_type == "this_month":
        clauses.append(f"{full_col} >= date_trunc('month', CURRENT_DATE)")
        clauses.append(f"{full_col} < (date_trunc('month', CURRENT_DATE) + INTERVAL '1 month')")

    # --- This year ---
    elif range_type == "this_year":
        clauses.append(f"{full_col} >= date_trunc('year', CURRENT_DATE)")
        clauses.append(f"{full_col} < (date_trunc('year', CURRENT_DATE) + INTERVAL '1 year')")

    # --- Last month ---
    elif range_type == "last_month":
        clauses.append(
            f"{full_col} >= (date_trunc('month', CURRENT_DATE) - INTERVAL '1 month')"
        )
        clauses.append(f"{full_col} < date_trunc('month', CURRENT_DATE)")

    # --- Last year ---
    elif range_type == "last_year":
        clauses.append(
            f"{full_col} >= (date_trunc('year', CURRENT_DATE) - INTERVAL '1 year')"
        )
        clauses.append(f"{full_col} < date_trunc('year', CURRENT_DATE)")

    # --- Absolute range ---
    elif range_type == "absolute_range":
        start_date = time_range.get("start_date")
        end_date = time_range.get("end_date")

        if not start_date or not end_date:
            raise ValueError("absolute_range requires start_date and end_date")

        clauses.append(f"{full_col} >= DATE '{start_date}'")
        clauses.append(f"{full_col} <= DATE '{end_date}'")

    else:
        raise ValueError(f"Unsupported time_range type: {range_type}")

    return {
        "time_column": full_col,
        "where_clauses": clauses
    }
