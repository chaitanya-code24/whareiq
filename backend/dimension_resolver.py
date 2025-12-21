from semantic_storage import load_semantic_mappings


# ---------------------------------
# Dimension Resolver (Storage-backed)
# ---------------------------------

def resolve_dimensions(plan: dict):
    """
    Resolves semantic dimensions into physical SQL select and group-by expressions.

    Input example:
    plan["dimensions"] = ["email", "name"]

    Output example:
    [
        {
            "logical_name": "email",
            "table": "users",
            "column": "email",
            "select_sql": "users.email AS email",
            "group_by_sql": "users.email"
        }
    ]
    """

    semantic_mappings = load_semantic_mappings()
    resolved_dimensions = []

    dimensions = plan.get("dimensions", [])

    # If there are no dimensions in the plan, nothing to resolve
    if not dimensions:
        return resolved_dimensions

    for logical_dim in dimensions:
        logical_name = logical_dim.lower()

        found_table = None
        found_column = None

        # Search across all tables for this logical dimension
        for table_name, meta in semantic_mappings.items():
            table_dimensions = meta.get("dimensions", {})

            if logical_name in table_dimensions:
                # Ambiguity check (same logical dim in multiple tables)
                if found_table is not None:
                    raise ValueError(
                        f"Dimension '{logical_name}' is defined in multiple tables "
                        f"('{found_table}' and '{table_name}'). Resolution is ambiguous."
                    )

                found_table = table_name
                found_column = table_dimensions[logical_name]

        # Not found anywhere → fail early
        if found_table is None or found_column is None:
            raise ValueError(
                f"Dimension '{logical_name}' could not be resolved to any physical column "
                f"using stored semantic mappings."
            )

        resolved_dimensions.append({
            "logical_name": logical_name,
            "table": found_table,
            "column": found_column,
            "select_sql": f"{found_table}.{found_column} AS {logical_name}",
            "group_by_sql": f"{found_table}.{found_column}"
        })

    return resolved_dimensions
