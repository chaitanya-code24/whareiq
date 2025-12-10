from schema_reader import load_physical_schema


# ---------------------------------
# Join Resolver (FK-only, storage-backed schema)
# ---------------------------------

def build_join_plan(resolved_measures: list, resolved_dimensions: list):
    """
    Build a FROM + JOIN plan based on resolved measures and dimensions
    and the physical foreign key graph from PostgreSQL.

    Inputs:
      - resolved_measures: list of dicts from resolve_measures()
      - resolved_dimensions: list of dicts from resolve_dimensions()

    Output example (for multi-table case):
      {
        "base_table": "orders",
        "joins": [
          {
            "left_table": "orders",
            "right_table": "users",
            "condition": "orders.user_id = users.id",
            "join_type": "INNER"
          }
        ],
        "from_sql": "orders INNER JOIN users ON orders.user_id = users.id"
      }

    For your current schema (only 'users' table), this will return:

      {
        "base_table": "users",
        "joins": [],
        "from_sql": "users"
      }
    """

    physical_schema = load_physical_schema()

    # ---------------------------------
    # 1. Collect all involved tables
    # ---------------------------------
    involved_tables = set()

    for m in resolved_measures:
        involved_tables.add(m["table"])

    for d in resolved_dimensions:
        involved_tables.add(d["table"])

    # If nothing is involved, we can't build a join plan
    if not involved_tables:
        return {
            "base_table": None,
            "joins": [],
            "from_sql": ""
        }

    # If only one table is involved, no joins are needed
    if len(involved_tables) == 1:
        base_table = next(iter(involved_tables))
        return {
            "base_table": base_table,
            "joins": [],
            "from_sql": base_table
        }

    # ---------------------------------
    # 2. Build FK-based adjacency graph between tables
    # ---------------------------------
    # adjacency: table_name -> list of (neighbor_table, join_condition)
    adjacency = {table: [] for table in physical_schema.keys()}

    for table, meta in physical_schema.items():
        fks = meta.get("foreign_keys", {})

        for col, fk in fks.items():
            ref_table = fk["references_table"]
            ref_col = fk["references_column"]

            # edge: table -> ref_table
            condition = f"{table}.{col} = {ref_table}.{ref_col}"

            if table not in adjacency:
                adjacency[table] = []
            if ref_table not in adjacency:
                adjacency[ref_table] = []

            # undirected graph for connectivity, but condition stored once
            adjacency[table].append((ref_table, condition))
            adjacency[ref_table].append((table, condition))

    # ---------------------------------
    # 3. BFS to find join paths connecting all involved tables
    # ---------------------------------
    involved_tables = list(involved_tables)
    start_table = involved_tables[0]

    from collections import deque

    queue = deque([start_table])
    parent = {start_table: None}
    edge_to_parent = {}  # child_table -> (parent_table, condition)

    while queue:
        current = queue.popleft()
        for neighbor, condition in adjacency.get(current, []):
            if neighbor not in parent:
                parent[neighbor] = current
                edge_to_parent[neighbor] = (current, condition)
                queue.append(neighbor)

    # Ensure all involved tables are reachable
    for table in involved_tables:
        if table not in parent:
            raise ValueError(
                f"Cannot build a deterministic join path: table '{table}' "
                f"is not connected via foreign keys to '{start_table}'."
            )

    # ---------------------------------
    # 4. Build join edges from BFS tree
    # ---------------------------------
    # We may include intermediate tables (bridge tables) if needed.
    join_edges = set()  # use set to avoid duplicates

    for table in parent:
        if table == start_table:
            continue
        if table not in edge_to_parent:
            continue

        parent_table, condition = edge_to_parent[table]

        # Normalize edge key so A-B and B-A are treated the same
        key = tuple(sorted([table, parent_table]) + [condition])

        join_edges.add((parent_table, table, condition, key))

    # ---------------------------------
    # 5. Construct JOIN clauses
    # ---------------------------------
    joins = []
    used_edges = set()

    for parent_table, child_table, condition, key in join_edges:
        if key in used_edges:
            continue
        used_edges.add(key)

        joins.append({
            "left_table": parent_table,
            "right_table": child_table,
            "condition": condition,
            "join_type": "INNER"
        })

    # Build FROM SQL
    from_sql = start_table
    for j in joins:
        from_sql += f" INNER JOIN {j['right_table']} ON {j['condition']}"

    return {
        "base_table": start_table,
        "joins": joins,
        "from_sql": from_sql
    }
