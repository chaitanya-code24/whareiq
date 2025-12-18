from src.dimension_resolver import resolve_dimensions

# Fake semantic plan using your existing dimensions
test_plan = {
    "dimensions": ["email", "name"]
}

try:
    result = resolve_dimensions(test_plan)
    print("\n✅ DIMENSION RESOLUTION OUTPUT:\n", result)

except Exception as e:
    print("❌ Dimension resolution failed:", e)
