def generate_answer(plan: dict, rows: list):
    if not rows:
        return "No results found."

    if plan.get("intent") == "count":
        return f"The result is {rows[0][0]}."

    return f"Returned {len(rows)} rows."
