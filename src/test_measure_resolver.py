from measure_resolver import resolve_measures

# Fake semantic plan for now – no measures yet
test_plan = {
    "measures": []
}

try:
    result = resolve_measures(test_plan)
    print("\n✅ MEASURE RESOLUTION OUTPUT:\n", result)

except Exception as e:
    print("❌ Measure resolution failed:", e)
