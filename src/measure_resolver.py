from semantic_storage import load_semantic_mappings


# ---------------------------------
# Measure Resolver (Storage-backed)
# ---------------------------------

def resolve_measures(plan: dict):
    """
    Resolves semantic measures from a WhareIQ plan into physical SQL expressions.

    Input example (from planner):

    plan["measures"] = [
        { "name": "revenue", "operation": "sum" }
    ]

    Using semantic mappings stored in PostgreSQL, we resolve:

    - Which table the metric belongs to
    - Which physical column implements it
    - Which SQL aggregation to apply

    Output example:

    [
        {
            "logical_name": "revenue",
            "operation": "sum",
            "table": "orders",
            "column": "total_amount",
            "sql": "SUM(orders.total_amount) AS revenue"
        }
    ]
    """

    semantic_mappings = load_semantic_mappings()
    resolved_measures = []

    measures = plan.get("measures", [])

    # If there are no measures in the plan, nothing to resolve
    if not measures:
        return resolved_measures

    for measure in measures:
        logical_name = measure["name"].lower()
        operation = measure["operation"].lower()

        found_table = None
        found_column = None

        # Search across all tables stored in semantic_mappings
        for table_name, meta in semantic_mappings.items():
            table_measures = meta.get("measures", {})

            # measures is a dict: { logical_metric_name: physical_column_name }
            if logical_name in table_measures:
                # If already found once in another table -> ambiguous
                if found_table is not None:
                    raise ValueError(
                        f"Measure '{logical_name}' is defined in multiple tables "
                        f"('{found_table}' and '{table_name}'). Resolution is ambiguous."
                    )

                found_table = table_name
                found_column = table_measures[logical_name]

        # If not found at all → cannot resolve this measure
        if found_table is None or found_column is None:
            raise ValueError(
                f"Measure '{logical_name}' could not be resolved to any physical column "
                f"using stored semantic mappings."
            )

        sql_expr = f"{operation.upper()}({found_table}.{found_column}) AS {logical_name}"

        resolved_measures.append({
            "logical_name": logical_name,
            "operation": operation,
            "table": found_table,
            "column": found_column,
            "sql": sql_expr
        })

    return resolved_measures
