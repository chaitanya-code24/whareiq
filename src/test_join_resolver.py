from measure_resolver import resolve_measures
from dimension_resolver import resolve_dimensions
from join_resolver import build_join_plan

# For now your schema only has 'users' table with email + name
test_plan = {
    "measures": [],
    "dimensions": ["email", "name"]
}

try:
    resolved_dims = resolve_dimensions(test_plan)
    resolved_measures = resolve_measures(test_plan)

    join_plan = build_join_plan(resolved_measures, resolved_dims)

    print("\n✅ JOIN PLAN OUTPUT:\n")
    print(join_plan)

except Exception as e:
    print("❌ Join plan failed:", e)
